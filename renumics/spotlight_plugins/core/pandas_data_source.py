"""
access pandas DataFrame table data
"""

from pathlib import Path
from typing import Any, List, Union, cast

import datasets
import numpy as np
import pandas as pd

from renumics.spotlight import dtypes
from renumics.spotlight.backend.exceptions import DatasetColumnsNotUnique
from renumics.spotlight.data_source import ColumnMetadata, DataSource, datasource
from renumics.spotlight.data_source.exceptions import InvalidDataSource
from renumics.spotlight.dataset.exceptions import ColumnNotExistsError
from renumics.spotlight.io import prepare_hugging_face_dict, try_literal_eval


@datasource(pd.DataFrame)
@datasource(".csv")
@datasource(".parquet")
@datasource(".feather")
@datasource(".orc")
@datasource(Path)
class PandasDataSource(DataSource):
    """
    access pandas DataFrame table data
    """

    _generation_id: int
    _uid: str
    _df: pd.DataFrame
    _name: str
    _intermediate_dtypes: dtypes.DTypeMap

    def __init__(self, source: Union[Path, pd.DataFrame]):
        if isinstance(source, Path):
            self._name = source.name
            if source.is_dir():
                try:
                    hf_dataset = datasets.load_dataset(
                        "imagefolder", data_dir=source
                    ).cast_column("image", datasets.Image(decode=False))
                    splits = list(hf_dataset.keys())

                    if len(splits) == 1:
                        df = hf_dataset[splits[0]].to_pandas()
                    else:
                        split_dfs = []
                        for split in splits:
                            split_df = hf_dataset[split].to_pandas()
                            split_df["split"] = split
                            split_dfs.append(split_df)
                        df = pd.concat(split_dfs)

                    # convert ClassLabel columns to Categorical
                    for feature_name, feature_type in hf_dataset[
                        splits[0]
                    ].features.items():
                        if isinstance(feature_type, datasets.ClassLabel):
                            try:
                                df[feature_name] = pd.Categorical.from_codes(
                                    df[feature_name], categories=feature_type.names
                                )
                            except ValueError:
                                # The codes have wrong type.
                                # This happens when there are splits but no classes.
                                # load_dataset tries to add a label col for the splits.
                                # Just delete it.
                                del df[feature_name]
                except Exception as e:
                    raise InvalidDataSource() from e
            else:
                extension = source.suffix.lower()
                if extension == ".csv":
                    df = pd.read_csv(source)
                elif extension == ".parquet":
                    df = pd.read_parquet(source)
                elif extension == ".feather":
                    df = pd.read_feather(source)
                elif extension == ".orc":
                    df = pd.read_orc(source)
                else:
                    raise InvalidDataSource()
        else:
            df = cast(pd.DataFrame, source)
            self._name = "pd.DataFrame"

        if not df.columns.is_unique:
            raise DatasetColumnsNotUnique()
        self._generation_id = 0
        self._uid = str(id(df))
        self._df = df.convert_dtypes()
        self._intermediate_dtypes = {
            # TODO: convert column name
            col: _determine_intermediate_dtype(self._df[col])
            for col in self._df.columns
        }

    @property
    def column_names(self) -> List[str]:
        return [str(column) for column in self._df.columns]

    @property
    def df(self) -> pd.DataFrame:
        """
        Get **a copy** of the served `DataFrame`.
        """
        return self._df.copy()

    @property
    def intermediate_dtypes(self) -> dtypes.DTypeMap:
        return self._intermediate_dtypes

    def __len__(self) -> int:
        return len(self._df)

    @property
    def semantic_dtypes(self) -> dtypes.DTypeMap:
        return {}

    def get_generation_id(self) -> int:
        return self._generation_id

    def get_uid(self) -> str:
        return self._uid

    def get_name(self) -> str:
        return self._name

    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        column_index = self._parse_column_index(column_name)
        column: pd.Series = self._df[column_index].iloc[indices]
        if pd.api.types.is_bool_dtype(column):
            values = column.to_numpy(na_value=pd.NA)  # type: ignore
            na_mask = column.isna()
            if na_mask.any():
                values[na_mask] = None
            return values
        if pd.api.types.is_integer_dtype(column):
            values = column.to_numpy(na_value=pd.NA)  # type: ignore
            na_mask = column.isna()
            if na_mask.any():
                values[na_mask] = None
            return values
        if pd.api.types.is_float_dtype(column):
            values = column.to_numpy()
            na_mask = column.isna()
            if na_mask.any():
                values[na_mask] = None
            return values
        if pd.api.types.is_datetime64_any_dtype(column):
            return column.dt.tz_localize(None).to_numpy()
        if pd.api.types.is_categorical_dtype(column):
            return column.cat.codes.to_numpy()
        if pd.api.types.is_string_dtype(column):
            column = column.astype(object).mask(column.isna(), None)
            str_mask = column.map(type) == str
            column[str_mask] = column[str_mask].apply(try_literal_eval)
            dict_mask = column.map(type) == dict
            column[dict_mask] = column[dict_mask].apply(prepare_hugging_face_dict)
            return column.to_numpy()
        if pd.api.types.is_object_dtype(column):
            column = column.astype(object).mask(column.isna(), None)
            str_mask = column.map(type) == str
            column[str_mask] = column[str_mask].apply(try_literal_eval)
            dict_mask = column.map(type) == dict
            column[dict_mask] = column[dict_mask].apply(prepare_hugging_face_dict)
            return column.to_numpy()
        try:
            return column.astype(str).to_numpy()
        except (TypeError, ValueError):
            raise TypeError(
                f"`pandas` column with dtype {column.dtype} is not supported."
            )

    def get_column_metadata(self, _: str) -> ColumnMetadata:
        return ColumnMetadata(nullable=True, editable=True)

    def _parse_column_index(self, column_name: str) -> Any:
        column_names = self.column_names
        try:
            loc = self._df.columns.get_loc(column_name)
        except KeyError:
            ...
        else:
            if isinstance(self._df.columns, pd.MultiIndex):
                return self._df.columns[loc][0]
            return self._df.columns[loc]
        try:
            index = column_names.index(column_name)
        except ValueError as e:
            raise ColumnNotExistsError(
                f"Column '{column_name}' doesn't exist in the dataset."
            ) from e
        return self._df.columns[index]


def _determine_intermediate_dtype(column: pd.Series) -> dtypes.DType:
    if pd.api.types.is_bool_dtype(column):
        return dtypes.bool_dtype
    if pd.api.types.is_categorical_dtype(column):
        return dtypes.CategoryDType(
            {category: code for code, category in enumerate(column.cat.categories)}
        )
    if pd.api.types.is_integer_dtype(column):
        return dtypes.int_dtype
    if pd.api.types.is_float_dtype(column):
        return dtypes.float_dtype
    if pd.api.types.is_datetime64_any_dtype(column):
        return dtypes.datetime_dtype
    if pd.api.types.is_string_dtype(column):
        return dtypes.str_dtype
    return dtypes.mixed_dtype

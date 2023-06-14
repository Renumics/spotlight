"""
table api endpoints
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse, Response
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from renumics.spotlight.backend import create_datasource
from renumics.spotlight.backend.data_source import (
    Column as DatasetColumn,
    idx_column,
    last_edited_at_column,
    last_edited_by_column,
    sanitize_values,
)
from renumics.spotlight.backend.exceptions import FilebrowsingNotAllowed, InvalidPath
from renumics.spotlight.backend.types import SpotlightApp
from renumics.spotlight.dtypes.typing import get_column_type_name
from renumics.spotlight.io.path import is_path_relative_to
from renumics.spotlight.reporting import emit_timed_event

from renumics.spotlight.dtypes import (
    Audio,
    Embedding,
    Image,
    Mesh,
    Sequence1D,
    Video,
)


LAZY_DTYPES = [Embedding, Mesh, Image, Video, Sequence1D, np.ndarray, Audio]


def _isfalsy(value: Optional[np.ndarray]) -> bool:
    # pylint: disable=unneeded-not
    return value is None or not not value


def _isfalsy_array(value: Optional[np.ndarray]) -> bool:
    # pylint: disable=unneeded-not, use-implicit-booleaness-not-len
    return value is None or not not len(value)


class Column(BaseModel):
    """
    a single table column
    """

    # pylint: disable=too-few-public-methods

    name: str
    index: Optional[int]
    hidden: bool
    editable: bool
    optional: bool
    role: str
    values: List[Any]
    references: Optional[List[bool]]
    y_label: Optional[str]
    x_label: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    categories: Optional[Dict[str, int]]
    embedding_length: Optional[int]

    @classmethod
    def from_dataset_column(cls, column: DatasetColumn) -> "Column":
        """
        Instantiate column from a dataset column.
        """

        if column.type in LAZY_DTYPES:
            if column.type in [Sequence1D, np.ndarray, Embedding]:
                references = [_isfalsy_array(value) for value in column.values]
            else:
                references = [_isfalsy(value) for value in column.values]
        else:
            references = None

        if column.type == Embedding:
            values = [""] * len(column.values)
        else:
            values = sanitize_values(column.values)

        return cls(
            name=column.name,
            index=column.order,
            hidden=column.hidden,
            editable=column.editable,
            optional=column.optional,
            role=get_column_type_name(column.type),
            values=values,
            references=references,
            x_label=column.x_label,
            y_label=column.y_label,
            description=column.description,
            tags=column.tags,
            categories=column.categories,
            embedding_length=column.embedding_length,
        )


# pylint: disable=too-few-public-methods
class Table(BaseModel):
    """
    a table slice
    """

    uid: str
    filename: str
    columns: List[Column]
    max_rows_hit: bool
    max_columns_hit: bool
    generation_id: int


router = APIRouter()


@router.get(
    "/",
    response_model=Table,
    response_class=ORJSONResponse,
    tags=["table"],
    operation_id="get_table",
)
@emit_timed_event
def get_table(request: Request) -> ORJSONResponse:
    """
    table slice api endpoint
    """
    app: SpotlightApp = request.app
    table = app.data_source
    if table is None:
        return ORJSONResponse(
            Table(
                uid="",
                filename="",
                columns=[],
                max_rows_hit=False,
                max_columns_hit=False,
                generation_id=-1,
            ).dict()
        )

    columns = [table.get_column(name) for name in table.column_names]
    columns.extend(table.get_internal_columns())
    row_count = len(table)
    columns.append(idx_column(row_count))
    if not any(column.name == "__last_edited_at__" for column in columns):
        columns.append(last_edited_at_column(row_count, datetime.now()))
    if not any(column.name == "__last_edited_by__" for column in columns):
        columns.append(last_edited_by_column(row_count, app.username))

    return ORJSONResponse(
        Table(
            uid=table.get_uid(),
            filename=table.get_name(),
            columns=[Column.from_dataset_column(column) for column in columns],
            max_rows_hit=False,
            max_columns_hit=False,
            generation_id=table.get_generation_id(),
        ).dict()
    )


@router.get(
    "/{column}/{row}",
    tags=["table"],
    operation_id="get_cell",
)
async def get_table_cell(
    column: str, row: int, generation_id: int, request: Request
) -> Any:
    """
    table cell api endpoint
    """
    app: SpotlightApp = request.app
    table = app.data_source
    if table is None:
        return None
    table.check_generation_id(generation_id)

    cell_data = table.get_cell_data(column, row)
    value = sanitize_values(cell_data)

    if isinstance(value, (bytes, str)):
        return Response(value, media_type="application/octet-stream")

    return value


@router.get(
    "/{column}/{row}/waveform",
    response_model=Optional[List[float]],
    tags=["table"],
    operation_id="get_waveform",
)
async def get_waveform(
    column: str, row: int, generation_id: int, request: Request
) -> Optional[List[float]]:
    """
    table cell api endpoint
    """
    app: SpotlightApp = request.app
    table = app.data_source
    if table is None:
        return None
    table.check_generation_id(generation_id)

    waveform = table.get_waveform(column, row)

    return sanitize_values(waveform)


class AddColumnRequest(BaseModel):
    """
    Add Column request model
    """

    dtype: str


@router.post("/open/{path:path}", tags=["table"], operation_id="open")
async def open_table(path: str, request: Request) -> None:
    """
    Open the specified table file

    :raises InvalidPath: if the supplied path is outside the project root
                         or points to an incompatible file
    """
    app: SpotlightApp = request.app

    if not app.filebrowsing_allowed:
        raise FilebrowsingNotAllowed()

    full_path = Path(app.project_root) / path

    # assert that the path is inside our project root
    if not is_path_relative_to(full_path, app.project_root):
        raise InvalidPath(path)

    app.data_source = create_datasource(full_path, dtype=app.dtype)

import * as React from 'react';
import { FunctionComponent, useEffect, useMemo, useState } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import { DataColumn, IndexArray } from '../../types';

type ColumnContextState = {
    columns: DataColumn[];
    columnVisibilities: Map<string, boolean>;
    setColumnVisibilities: React.Dispatch<React.SetStateAction<Map<string, boolean>>>;
    rowIndices: IndexArray;
};

export const DataContext = React.createContext<ColumnContextState>({
    columns: [],
    columnVisibilities: new Map(),
    setColumnVisibilities: () => null,
    rowIndices: new Int32Array(),
});

const columnsSelector = (d: Dataset) => d.columns;
const selectedIndicesSelector = (d: Dataset) => d.selectedIndices;

// column types that should be visible by default
const columnVisibleByDefault = (column: DataColumn) =>
    ['Mesh', 'Sequence1D', 'Image'].includes(column.type.kind);

export const DataProvider: FunctionComponent<{ children: React.ReactNode }> = ({
    children,
}) => {
    const columns = useDataset(columnsSelector);
    const rowIndices = useDataset(selectedIndicesSelector);

    // store a map from column names to visibilities to enable the selection of visible columns
    const [columnVisibilities, setColumnVisibilities] = useState(
        new Map<string, boolean>()
    );

    // update visible columns if the dataset's columns change
    useEffect(() => {
        setColumnVisibilities((previousVisibilities) => {
            const newVisibilities = new Map(previousVisibilities);
            columns.forEach((column) =>
                newVisibilities.set(
                    column.key,
                    newVisibilities.get(column.key) ?? columnVisibleByDefault(column)
                )
            );
            return newVisibilities;
        });
    }, [columns]);

    // prepare visible rows and columns for easy access in jsx
    const visibleColumns = useMemo(
        () => columns.filter((column) => columnVisibilities.get(column.key)),
        [columns, columnVisibilities]
    );

    return (
        <DataContext.Provider
            value={{
                columns: visibleColumns,
                rowIndices,
                columnVisibilities,
                setColumnVisibilities,
            }}
        >
            {children}
        </DataContext.Provider>
    );
};

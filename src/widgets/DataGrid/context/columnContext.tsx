import _ from 'lodash';
import * as React from 'react';
import { FunctionComponent, useCallback, useContext, useMemo } from 'react';
import { CallbackOrData, Dataset, useDataset } from '../../../stores/dataset';
import { DataColumn } from '../../../types';
import { shallow } from 'zustand/shallow';
import columnWidthByType from '../columnWidthByType';

type ColumnContextState = {
    allColumns: DataColumn[];
    columns: DataColumn[];
    hideColumn: (columnKey: string) => void;
    setColumnKeys: (columns: CallbackOrData<string[]>) => void;
    areOrderedByRelevance: boolean;
    setAreOrderedByRelevance: (areOrderedByRelevance: boolean) => void;
    resetColumns: () => void;
};

export const ColumnContext = React.createContext<ColumnContextState>({
    allColumns: [],
    columns: [],
    hideColumn: () => undefined,
    setColumnKeys: () => undefined,
    resetColumns: () => undefined,
    areOrderedByRelevance: false,
    setAreOrderedByRelevance: () => undefined,
});

const allColumnsSelector = (d: Dataset) => d.columns;

type Props = {
    columnKeys: string[];
    setColumnKeys: (keys: CallbackOrData<string[]>) => void;
    areOrderedByRelevance: boolean;
    setAreOrderedByRelevance: (areOrderedByRelevance: boolean) => void;
    resetColumns: () => void;
};

export const ColumnProvider: FunctionComponent<
    Props & { children: React.ReactNode }
> = ({ children, ...props }) => {
    const {
        columnKeys,
        setColumnKeys,
        areOrderedByRelevance,
        setAreOrderedByRelevance,
        resetColumns,
    } = props;

    const allColumns = useDataset(allColumnsSelector);
    const columns = useMemo(
        () => allColumns.filter(({ key }) => columnKeys.includes(key)),
        [allColumns, columnKeys]
    );

    const sortedColumnsSelector = useCallback(
        (d: Dataset) => {
            if (areOrderedByRelevance) {
                return _.orderBy(
                    columns,
                    (column) => d.columnRelevance.get(column.key) || -Infinity,
                    'desc'
                );
            } else {
                return columns;
            }
        },
        [areOrderedByRelevance, columns]
    );

    const sortedColumns = useDataset(sortedColumnsSelector, shallow);

    const hideColumn = useCallback(
        (columnKey: string) => {
            setColumnKeys((columnKeys) =>
                columnKeys.filter((key) => key !== columnKey)
            );
        },
        [setColumnKeys]
    );

    return (
        <ColumnContext.Provider
            value={{
                allColumns,
                columns: sortedColumns,
                setColumnKeys,
                hideColumn,
                areOrderedByRelevance,
                setAreOrderedByRelevance,
                resetColumns,
            }}
        >
            {children}
        </ColumnContext.Provider>
    );
};

export const useOrderColumnsByRelevance = (): [
    ColumnContextState['areOrderedByRelevance'],
    ColumnContextState['setAreOrderedByRelevance']
] => {
    const { areOrderedByRelevance, setAreOrderedByRelevance } =
        useContext(ColumnContext);
    return [areOrderedByRelevance, setAreOrderedByRelevance];
};

export const useVisibleColumns = (): [
    ColumnContextState['columns'],
    ColumnContextState['setColumnKeys'],
    ColumnContextState['hideColumn'],
    ColumnContextState['resetColumns']
] => {
    const { setColumnKeys, columns, hideColumn, resetColumns } =
        useContext(ColumnContext);
    return [columns, setColumnKeys, hideColumn, resetColumns];
};

export const useColumn = (index: number): DataColumn => {
    const context = useContext(ColumnContext);
    return context.columns[index];
};

export const useColumns = (): DataColumn[] => {
    const context = useContext(ColumnContext);
    return context.columns;
};

export const useColumnWidth = (): ((index: number) => number) => {
    const context = useContext(ColumnContext);
    return useCallback(
        (index: number) => columnWidthByType[context.columns[index].type.kind],
        [context.columns]
    );
};

export const useColumnCount = (): number => {
    const context = useContext(ColumnContext);
    return context.columns.length;
};

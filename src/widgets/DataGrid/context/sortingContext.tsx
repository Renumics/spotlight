import * as React from 'react';
import { FunctionComponent, useCallback, useContext, useMemo } from 'react';
import { Dataset, Sorting, useDataset } from '../../../stores/dataset';
import { TableData } from '../../../types';
import { useTableView } from './tableViewContext';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const isNothing = (value: any) => {
    return value === null || Number.isNaN(value);
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const compareRowValues = (a: any, b: any) => {
    if (a instanceof Array && b instanceof Array) {
        for (let i = 0; i < a.length; ++i) {
            if (a[i] > b[i]) return 1;
            if (a[i] < b[i]) return -1;
        }
        return 0;
    }
    // value > undefined (lazy value) > nothing (null/NaN)
    if (isNothing(b) && !isNothing(a)) return 1;
    if (isNothing(a) && !isNothing(b)) return -1;
    if (b === undefined && a !== undefined) return 1;
    if (a === undefined && b !== undefined) return -1;
    if (a > b) return 1;
    if (b > a) return -1;
    return 0;
};

const sortIndices = (
    data: TableData,
    indices: ArrayLike<number>,
    sortColumns: [string, Sorting][]
): Int32Array => {
    const sortKeys = sortColumns.map(([columnKey, sorting]): [string, number] => [
        columnKey,
        sorting === 'ASC' ? 1 : -1,
    ]);

    return new Int32Array(indices).sort((a, b) => {
        let comp = 0;
        let sortingIndex = 0;

        while (comp === 0 && sortingIndex < sortKeys.length) {
            const [key, dir] = sortKeys[sortingIndex];
            sortingIndex += 1;
            comp = dir * compareRowValues(data[key]?.[a], data[key]?.[b]);
        }
        return comp;
    });
};

type SortingContextState = {
    sorting: [string, Sorting][];
    setSorting: React.Dispatch<React.SetStateAction<[string, Sorting][]>>;
    sortedIndices: Int32Array;
    getOriginalIndex: (sortedIndex: number) => number;
    getSortedIndex: (originalIndex: number) => number;
};

export const SortingContext = React.createContext<SortingContextState>({
    sorting: [],
    setSorting: () => null,
    sortedIndices: new Int32Array(),
    getOriginalIndex: () => 0,
    getSortedIndex: () => 0,
});

const dataSelector = (d: Dataset) => d.columnData;
const indicesSelector = (d: Dataset) => d.indices;
const filteredIndicesSelector = (d: Dataset) => d.filteredIndices;
const selectedIndicesSelector = (d: Dataset) => d.selectedIndices;

export const SortingProvider: FunctionComponent<
    Pick<SortingContextState, 'sorting' | 'setSorting'> & { children: React.ReactNode }
> = ({ sorting, setSorting, children }) => {
    const { tableView } = useTableView();
    const data = useDataset(dataSelector);
    const allIndices = useDataset(indicesSelector);
    const filteredIndices = useDataset(filteredIndicesSelector);
    const selectedIndices = useDataset(selectedIndicesSelector);

    const indices =
        tableView === 'filtered'
            ? filteredIndices
            : tableView === 'selected'
              ? selectedIndices
              : allIndices;

    const sortedIndices = useMemo(
        () => sortIndices(data, indices, sorting),
        [data, indices, sorting]
    );

    const reverseSortedIndices = useMemo(() => {
        const reverse = Array(sortedIndices.length).fill(0);
        for (let i = 0; i < sortedIndices.length; i++) {
            reverse[sortedIndices[i]] = i;
        }
        return reverse;
    }, [sortedIndices]);

    const getOriginalIndex = useCallback(
        (sortedIndex: number) => sortedIndices[sortedIndex],
        [sortedIndices]
    );

    const getSortedIndex = useCallback(
        (originaIndex: number) => reverseSortedIndices[originaIndex],
        [reverseSortedIndices]
    );

    return (
        <SortingContext.Provider
            value={{
                sorting,
                setSorting,
                sortedIndices,
                getOriginalIndex,
                getSortedIndex,
            }}
        >
            {children}
        </SortingContext.Provider>
    );
};

export const useSortings = (): [string, Sorting][] => {
    const { sorting } = useContext(SortingContext);
    return sorting;
};

export const useSortByColumn = (
    columnKey: string
): [Sorting | undefined, (sorting?: Sorting | undefined) => void, () => void] => {
    const { sorting, setSorting } = useContext(SortingContext);
    const columnSorting = useMemo(
        () => sorting.find(([key]) => key === columnKey)?.[1] || undefined,
        [sorting, columnKey]
    );

    const sortBy = useCallback(
        (sorting?: Sorting) => {
            setSorting((sortings) => {
                const newSortings =
                    sortings?.filter(([key]) => key !== columnKey) || [];
                if (sorting) newSortings.unshift([columnKey, sorting]);
                return newSortings;
            });
        },
        [setSorting, columnKey]
    );

    const resetSorting = useCallback(() => setSorting([]), [setSorting]);

    return [columnSorting, sortBy, resetSorting];
};

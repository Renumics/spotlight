import * as Comlink from 'comlink';
import { DataType, isCategorical, isScalar } from '../../datatypes';
import { TransferFunction } from '../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { useColors } from '../colors';
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { shallow } from 'zustand/shallow';
import { Table } from '../../client';
import {
    ColumnsStats,
    DataColumn,
    DataFrame,
    DataRow,
    DataIssue as DataIssue,
    Filter,
    IndexArray,
    TableData,
} from '../../types';
import api from '../../api';
import { notifyAPIError, notifyError } from '../../notify';
import { makeColumnsColorTransferFunctions } from './colorTransferFunctionFactory';
import { makeColumn } from './columnFactory';
import { makeColumnsStats } from './statisticsFactory';

export type CallbackOrData<T> = ((data: T) => T) | T;

export type Sorting = 'DESC' | 'ASC';
export type DataSelector = 'full' | 'filtered' | 'selected';

export interface Dataset {
    uid?: string; // UID of the dataset
    generationID: number;
    filename?: string; // filename of the dataset
    loading: boolean; // are we currently loading the Dataset
    columnStats: { full: ColumnsStats; selected: ColumnsStats; filtered: ColumnsStats }; // an object storing statistics for available columns
    columns: DataColumn[];
    columnsByKey: Record<string, DataColumn>;
    columnData: TableData;
    isAnalysisRunning: boolean;
    issues: DataIssue[];
    rowsWithIssues: IndexArray;
    colorTransferFunctions: Record<
        string,
        {
            full: TransferFunction[];
            filtered: TransferFunction[];
        }
    >;
    recomputeColorTransferFunctions: () => void;
    length: number;
    indices: Int32Array;
    getRow: (index: number) => DataRow;
    isIndexSelected: boolean[]; // an array indicating for each row index if the corresponding row is selected will be computed based on selectedIndices
    selectedIndices: Int32Array;
    isIndexHighlighted: boolean[]; // an array indicating if the corresponding row is currently highlighted
    highlightedIndices: Int32Array;
    isIndexFiltered: boolean[]; // an array indicating for each row index if the corresponding row is filtered will be computed based on filteredIndices
    filteredIndices: Int32Array;
    sortColumns: Map<DataColumn, Sorting>;
    sortBy: (column?: DataColumn, sorting?: Sorting) => void;
    columnRelevance: Map<string, number>;
    columnRelevanceGeneration: number;
    filters: Filter[]; // the currently applied filters
    tags: string[]; // all unique column tags
    lastFocusedRow?: number; // the last row that has been focused by a view
    openTable: (path: string) => void; //open the table file at path
    fetch: () => void; // fetch the dataset from the backend
    fetchIssues: () => void; // fetch the ready issues
    refresh: () => void; // refresh the dataset from the backend
    addFilter: (filter: Filter) => void; // add a new filter
    removeFilter: (filter: Filter) => void; // remove an existing filter
    toggleFilterEnabled: (filter: Filter) => void; // toggle filter isEnabled
    replaceFilter: (filter: Filter, newFilter: Filter) => void; // replace an existing filter
    selectRows: (rows: CallbackOrData<IndexArray>) => void; // select a set of rows
    setHighlightedRows: (mask: boolean[]) => void;
    highlightRowAt: (rowIndex: number, only?: boolean) => void;
    highlightRows: (rows: CallbackOrData<IndexArray>) => void;
    dehighlightRowAt: (rowIndex: number) => void;
    dehighlightAll: () => void;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    relevanceWorker: any;
    isComputingRelevance: boolean;
    recomputeColumnRelevance: () => void;
    focusRow: (row?: number) => void;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function convertValue(value: any, type: DataType) {
    if (type.kind === 'float' && value === null) {
        return NaN;
    }

    if (value === null) return null;

    if (type.kind === 'datetime') {
        return new Date(Date.parse(value));
    }

    if (type.kind === 'Window') {
        value[0] = value[0] === null ? NaN : value[0];
        value[1] = value[1] === null ? NaN : value[1];
        return value;
    }

    return value;
}

const fetchTable = async (): Promise<{
    uid: string;
    generationID: number;
    filename: string;
    dataframe: DataFrame;
}> => {
    let table: Table;

    try {
        table = await api.table.getTable();
    } catch (error) {
        notifyAPIError(error);
        return {
            uid: '',
            generationID: -1,
            filename: '',
            dataframe: {
                columns: [],
                length: 0,
                data: {},
            },
        };
    }

    const columns = table.columns.map(makeColumn);
    const columnData: TableData = {};
    table.columns.forEach((rawColumn, i) => {
        const dsColumn = columns[i];
        if (rawColumn.values === undefined) {
            return;
        }

        columnData[dsColumn.key] = rawColumn.values.map((value) =>
            convertValue(value, dsColumn.type)
        );

        switch (dsColumn.type.kind) {
            case 'int':
            case 'Category':
                columnData[dsColumn.key] = Int32Array.from(columnData[dsColumn.key]);
                break;
            case 'float':
                columnData[dsColumn.key] = Float32Array.from(columnData[dsColumn.key]);
                break;
        }
    });

    const length = _.max(table.columns.map((col) => col.values?.length ?? 0)) ?? 0;

    const dataframe: DataFrame = {
        columns,
        length,
        data: columnData,
    };
    return {
        uid: table.uid,
        generationID: table.generationId,
        filename: table.filename,
        dataframe,
    };
};

export const useDataset = create(
    subscribeWithSelector<Dataset>((set, get) => {
        return {
            loading: false,
            uid: '',
            generationID: -1,
            columns: [],
            columnsByKey: {},
            columnData: {},
            length: 0,
            issues: [],
            rowsWithIssues: [],
            isAnalysisRunning: false,
            indices: new Int32Array(),
            columnStats: { full: {}, filtered: {}, selected: {} },
            colorTransferFunctions: {},
            isIndexSelected: [],
            selectedIndices: new Int32Array(),
            isIndexHighlighted: [],
            highlightedIndices: new Int32Array(),
            isIndexFiltered: [],
            filteredIndices: new Int32Array(),
            sortColumns: new Map<DataColumn, Sorting>(),
            sortBy: (column?: DataColumn, sorting?: Sorting) => {
                set((d) => {
                    if (column === undefined) {
                        return { sortColumns: new Map<DataColumn, Sorting>() };
                    } else {
                        const newSortColumns = new Map<DataColumn, Sorting>(
                            d.sortColumns
                        );
                        newSortColumns.delete(column);
                        if (sorting !== undefined) newSortColumns.set(column, sorting);

                        return { sortColumns: newSortColumns };
                    }
                });
            },
            columnRelevance: new Map<string, number>(),
            columnRelevanceGeneration: 0,
            filters: [],
            tags: [],
            openTable: async (path: string) => {
                api.table.open({ path }).then(() => get().fetch());
            },
            fetch: async () => {
                set(() => ({
                    loading: true,
                    columns: [],
                    columnsByKey: {},
                    length: 0,
                    indices: new Int32Array(),
                    isIndexSelected: [],
                    selectedIndices: new Int32Array(),
                    isIndexHighlighted: [],
                    highlightedIndices: new Int32Array(),
                    filteredIndices: new Int32Array(),
                    sortColumns: new Map<DataColumn, Sorting>(),
                    columnRelevance: new Map<string, number>(),
                    filters: [],
                    issues: [],
                    rowsWithIssues: [],
                    isAnalysisRunning: true,
                }));

                const tableFetcher = fetchTable();
                const { uid, generationID, filename, dataframe } = await tableFetcher;

                const columnStats = {
                    full: makeColumnsStats(dataframe.columns, dataframe.data),
                    selected: {},
                    filtered: {},
                };

                set(() => ({
                    uid,
                    generationID,
                    filename,
                    length: dataframe.length,
                    loading: false,
                    columns: dataframe.columns,
                    columnsByKey: _.keyBy(dataframe.columns, 'key'),
                    columnData: dataframe.data,
                    columnStats,
                }));
            },
            fetchIssues: async () => {
                const analysis = await api.issues.getAll();
                const rowsWithIssues = new Set<number>();
                for (const issue of analysis.issues) {
                    issue.rows.forEach(rowsWithIssues.add, rowsWithIssues);
                }
                set({
                    issues: analysis.issues as DataIssue[],
                    rowsWithIssues: Int32Array.from(rowsWithIssues),
                    isAnalysisRunning: analysis.running,
                });
            },
            refresh: async () => {
                const { uid, generationID, filename, dataframe } = await fetchTable();
                const columnStats = {
                    full: makeColumnsStats(dataframe.columns, dataframe.data),
                    selected: {},
                    filtered: {},
                };
                set(() => ({
                    uid,
                    generationID,
                    filename,
                    length: dataframe.length,
                    loading: false,
                    columns: dataframe.columns,
                    columnsByKey: _.keyBy(dataframe.columns, 'key'),
                    columnData: dataframe.data,
                    columnStats,
                }));
            },
            getRow: (index: number) => {
                const state = get();

                const values: DataRow['values'] = {};
                state.columns.forEach((col) => {
                    values[col.key] = state.columnData[index];
                });

                return {
                    index,
                    values,
                };
            },
            addFilter: (filter) => {
                set((d) => ({ filters: [...d.filters, filter] }));
            },
            removeFilter: (filter) => {
                set((d) => ({
                    filters: _.filter(d.filters, (f) => f !== filter),
                }));
            },
            toggleFilterEnabled: (filter) => {
                set((d) => {
                    const filterIndex = d.filters.indexOf(filter);
                    const filters = d.filters.slice();
                    filters[filterIndex].isEnabled = !filter.isEnabled;
                    return { filters };
                });
            },
            replaceFilter: (filter, newFilter) => {
                set((d) => {
                    const filterIndex = d.filters.indexOf(filter);
                    const filters = d.filters.slice();
                    filters[filterIndex] = newFilter;
                    return { filters };
                });
            },
            selectRows: (rowIndices) => {
                const selectedIndices = Int32Array.from(
                    typeof rowIndices === 'function'
                        ? rowIndices(get().selectedIndices)
                        : rowIndices
                );

                const isIndexSelected = new Array(get().length).fill(false);
                selectedIndices.forEach((index) => (isIndexSelected[index] = true));

                set(() => ({ isIndexSelected, selectedIndices }));
            },
            setHighlightedRows: (mask) => {
                const highlightedIndices: number[] = [];
                mask.forEach((highlighted, index) => {
                    if (highlighted) {
                        highlightedIndices.push(index);
                    }
                });
                set(() => ({
                    isIndexHighlighted: mask,
                    highlightedIndices: Int32Array.from(highlightedIndices),
                }));
            },
            highlightRows: (rowIndicesOrCallback) => {
                const rowIndices =
                    typeof rowIndicesOrCallback === 'function'
                        ? rowIndicesOrCallback(get().selectedIndices)
                        : rowIndicesOrCallback;
                const mask = new Array(get().length).fill(false);
                rowIndices.forEach((index: number) => (mask[index] = true));
                get().setHighlightedRows(mask);
            },
            highlightRowAt: (rowIndex, only = false) => {
                // early out if the index is highlighted anyway
                if (get().isIndexHighlighted[rowIndex]) return;

                const newHighlights = only
                    ? new Array(get().length).fill(false)
                    : get().isIndexHighlighted.slice();
                newHighlights[rowIndex] = true;
                get().setHighlightedRows(newHighlights);
            },
            dehighlightRowAt: (rowIndex) => {
                // early out if the index is not highlighted anyway
                if (!get().isIndexHighlighted[rowIndex]) return;

                const newHighlights = get().isIndexHighlighted.slice();
                newHighlights[rowIndex] = false;
                get().setHighlightedRows(newHighlights);
            },
            dehighlightAll: () => {
                // early out if nothing is highlighted anyway
                if (!get().isIndexHighlighted.some((v) => v)) return;

                const newHighlights = new Array(get().length).fill(false);
                get().setHighlightedRows(newHighlights);
            },
            focusRow: (row?: number) => {
                set({ lastFocusedRow: row });
            },
            relevanceWorker: Comlink.wrap(
                new Worker(new URL('./relevanceWorker.ts', import.meta.url), {
                    type: 'module',
                })
            ),
            isComputingRelevance: false,
            recomputeColumnRelevance: async () => {
                const state = get();

                if (state.isComputingRelevance) {
                    set({
                        columnRelevanceGeneration: state.columnRelevanceGeneration + 1,
                    });
                    return;
                }

                set({
                    isComputingRelevance: true,
                    columnRelevance: new Map<string, number>(),
                    columnRelevanceGeneration: state.columnRelevanceGeneration + 1,
                });

                let columnRelevance = new Map<string, number>();

                let gen = 0;
                do {
                    gen = get().columnRelevanceGeneration;

                    columnRelevance = await state.relevanceWorker.computeRelevances(
                        state.columns,
                        state.columnData,
                        state.selectedIndices,
                        state.filteredIndices
                    );
                } while (gen !== get().columnRelevanceGeneration);

                set({ columnRelevance, isComputingRelevance: false });
            },
            recomputeColorTransferFunctions: async () => {
                const columnsToCompute = get()
                    .columns.filter(
                        (c) =>
                            !c.isInternal && (isScalar(c.type) || isCategorical(c.type))
                    )
                    .map((c) => c.key);

                const newTransferFunctions = makeColumnsColorTransferFunctions(
                    get().columns.filter(({ key }) => columnsToCompute.includes(key)),
                    get().columnData,
                    get().columnStats,
                    get().isIndexFiltered
                );

                set({
                    colorTransferFunctions: newTransferFunctions,
                });
            },
        };
    })
);

useDataset.subscribe(
    (state) => state.length,
    (length: number) => {
        useDataset.setState({ indices: new Int32Array(Array(length).keys()) });
    },
    { fireImmediately: true }
);

useDataset.subscribe(
    (state) => state.columns,
    (columns: DataColumn[]) => {
        useDataset.setState({
            tags: _.uniq(columns.flatMap((column) => column.tags ?? [])),
        });
    }
);

useDataset.subscribe(
    (state) => ({
        length: state.length,
        filters: state.filters,
        columns: state.columns,
        data: state.columnData,
    }),
    ({ length, filters, columns, data }) => {
        const applyFilter = (filter: Filter, rowIndex: number) => {
            const inFilter = filter.apply(rowIndex, data);
            return !filter.isEnabled || (filter.isInverted ? !inFilter : inFilter);
        };

        const isIndexFiltered = Array(length);
        try {
            for (let i = 0; i < length; i++) {
                isIndexFiltered[i] = filters.every((filter) => {
                    try {
                        return applyFilter(filter, i);
                    } catch (error) {
                        useDataset.getState().removeFilter(filter);
                        throw error;
                    }
                });
            }
        } catch (error) {
            console.error(error);
            notifyError(`Error applying filter! '${error}'`);
        }
        const filteredIndices: number[] = [];
        isIndexFiltered.forEach((isFiltered, i) => {
            if (isFiltered) {
                filteredIndices.push(i);
            }
        });

        const filteredStats = makeColumnsStats(columns, data, isIndexFiltered);
        useDataset.setState((state) => ({
            isIndexFiltered,
            filteredIndices: Int32Array.from(filteredIndices),
            columnStats: { ...state.columnStats, filtered: filteredStats },
        }));
    },
    { equalityFn: shallow }
);

useDataset.subscribe(
    (state) => state.isIndexSelected,
    (newIndices: boolean[]) => {
        const columns = useDataset.getState().columns as DataColumn[];
        const columnData = useDataset.getState().columnData;

        if (columns === undefined) return;

        const stats = makeColumnsStats(columns, columnData, newIndices);
        useDataset.setState({
            columnStats: Object.assign(useDataset.getState().columnStats, {
                selected: stats,
            }),
        });
    }
);

useDataset.subscribe(
    (state) => state.columnData,
    useDataset.getState().recomputeColorTransferFunctions
);

useDataset.subscribe(
    (state) => state.filteredIndices,
    () => {
        useDataset.getState().recomputeColumnRelevance();
        useDataset.getState().recomputeColorTransferFunctions();
    }
);

useDataset.subscribe(
    (state) => state.selectedIndices,
    useDataset.getState().recomputeColumnRelevance
);

useColors.subscribe(() => useDataset.getState().recomputeColorTransferFunctions());

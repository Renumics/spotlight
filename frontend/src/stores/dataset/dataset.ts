import * as Comlink from 'comlink';
import { DataType, isCategorical, isScalar } from '../../datatypes';
import { TransferFunction } from '../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { useColors } from '../colors';
import create from 'zustand-store-addons';
import { Table } from '../../client';
import {
    ColumnsStats,
    DataColumn,
    DataFrame,
    DataRow,
    Filter,
    IndexArray,
    TableData,
} from '../../types';
import api from '../../api';
import { notify, notifyAPIError } from '../../notify';
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
    refresh: () => void; // refresh the dataset from the backend
    addFilter: (filter: Filter) => void; // add a new filter
    removeFilter: (filter: Filter) => void; // remove an existing filter
    toggleFilterEnabled: (filter: Filter) => void; // toggle filter isEnabled
    replaceFilter: (filter: Filter, newFilter: Filter) => void; // replace an existing filter
    selectRows: (rows: CallbackOrData<IndexArray>) => void; // select a set of rows
    setHighlightedRows: (mask: boolean[]) => void;
    highlightRowAt: (rowIndex: number, only?: boolean) => void;
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
    if (type.kind === 'datetime') {
        if (value?.length === 0) {
            return null;
        } else {
            return new Date(Date.parse(value));
        }
    }

    if (type.kind === 'float' && value === null) {
        return NaN;
    }

    if (type.kind === 'Window') {
        if (value[0] === null && value[1] === null) return null;
        value[0] = value[0] === null ? NaN : value[0];
        value[1] = value[1] === null ? NaN : value[1];
        return value;
    }

    return value;
}

export function compareColumnOrder(a: DataColumn, b: DataColumn) {
    if (a.isInternal && !b.isInternal) {
        return 1;
    } else if (b.isInternal && !a.isInternal) {
        return -1;
    } else if (a.order < b.order) {
        return 1;
    } else if (a.order > b.order) {
        return -1;
    }
    return a.name.localeCompare(b.name);
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

    // notify the user if a (demo) limit is hit
    if (table.maxColumnsHit) {
        notify('Columns in table exceed column limit.', 'warning');
    }
    if (table.maxRowsHit) {
        notify('Rows in table exceed wow limit.', 'warning');
    }

    const columns = table.columns.map(makeColumn);
    const columnData: TableData = {};
    table.columns.forEach((rawColumn, i) => {
        const dsColumn = columns[i];
        if (rawColumn.values === undefined) {
            return;
        }

        columnData[dsColumn.key] = rawColumn.values.map((value, index) =>
            convertValue(
                value !== null
                    ? value
                    : rawColumn.references?.[index]
                    ? undefined
                    : null,
                dsColumn.type
            )
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

    const sortedColumns = columns.sort(compareColumnOrder);

    const dataframe: DataFrame = {
        columns: sortedColumns,
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

export const useDataset = create<Dataset>(
    (set, get) => {
        return {
            loading: false,
            uid: '',
            generationID: -1,
            columns: [],
            columnsByKey: {},
            columnData: {},
            length: 0,
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
                    length: 0,
                    indices: new Int32Array(),
                    isIndexSelected: [],
                    selectedIndices: new Int32Array(),
                    isIndexHighlighted: [],
                    highlightedIndices: new Int32Array(),
                    isIndexFiltered: [],
                    filteredIndices: new Int32Array(),
                    sortColumns: new Map<DataColumn, Sorting>(),
                    columnRelevance: new Map<string, number>(),
                    filters: [],
                }));

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
                    columnData: dataframe.data,
                    columnStats,
                }));
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
    },
    {
        computed: {
            columnsByKey() {
                return _.keyBy(this.columns, 'key');
            },
            isIndexFiltered() {
                const filters = this.filters as Filter[];
                const data = this.columnData;
                const length = this.length;

                const applyFilter = (filter: Filter, rowIndex: number) => {
                    const inFilter = filter.apply(rowIndex, data);
                    return (
                        !filter.isEnabled || (filter.isInverted ? !inFilter : inFilter)
                    );
                };

                const filtered = Array(length);
                for (let i = 0; i < length; i++) {
                    filtered[i] = filters.every((filter) => applyFilter(filter, i));
                }
                return filtered;
            },
            tags() {
                return _.uniq(
                    this.columns.reduce((prev: string[], current: DataColumn) => {
                        current.tags?.forEach((t) => prev.push(t));
                        return prev;
                    }, [] as string[])
                );
            },
            indices() {
                return new Int32Array(this.length).map((_, i) => i);
            },
        },
        watchers: {
            isIndexFiltered(newIndices: boolean[]) {
                const columns = this.get().columns as DataColumn[];
                const columnData = this.get().columnData;

                if (columns === undefined) return;

                const filteredIndices: number[] = [];
                newIndices.forEach((isFiltered, i) => {
                    if (isFiltered) {
                        filteredIndices.push(i);
                    }
                });

                const stats = makeColumnsStats(columns, columnData, newIndices);

                this.set({
                    filteredIndices: Int32Array.from(filteredIndices),
                    columnStats: Object.assign(this.get().columnStats, {
                        filtered: stats,
                    }),
                });
            },
            columnData() {
                this.get().recomputeColorTransferFunctions();
            },
            isIndexSelected(newIndices: boolean[]) {
                const columns = this.get().columns as DataColumn[];
                const columnData = this.get().columnData;

                if (columns === undefined) return;

                const stats = makeColumnsStats(columns, columnData, newIndices);
                this.set({
                    columnStats: Object.assign(this.get().columnStats, {
                        selected: stats,
                    }),
                });
            },
            filteredIndices() {
                this.get().recomputeColumnRelevance();
                this.get().recomputeColorTransferFunctions();
            },
            selectedIndices() {
                this.get().recomputeColumnRelevance();
            },
        },
    }
);

useColors.subscribe(() => useDataset.getState().recomputeColorTransferFunctions());

import TableIcon from '../../icons/Table';
import { Widget } from '../types';
import { useCallback, useMemo, useRef } from 'react';
import AutoSizer from 'react-virtualized-auto-sizer';
import { VariableSizeGrid as Grid } from 'react-window';
import { Dataset, Sorting, useDataset } from '../../stores/dataset';
import tw from 'twin.macro';
import { DataColumn, TableView } from '../../types';
import getScrollbarSize from '../../browser';
import { shallow } from 'zustand/shallow';
import useWidgetConfig from '../useWidgetConfig';
import { ColumnProvider } from './context/columnContext';
import { SortingProvider } from './context/sortingContext';
import { TableViewProvider } from './context/tableViewContext';
import HeaderGrid from './HeaderGrid';
import MenuBar from './MenuBar';
import TableGrid from './TableGrid';

const headerHeight = 24;

const GridWrapper = tw.div`flex flex-col h-full w-full overflow-hidden`;
const AutoSizerWrapper = tw.div`flex-auto`;

const columnsSelector = (d: Dataset) => d.columns;

const columnVisibleByDefault = (column: DataColumn) =>
    !column.hidden &&
    ['float', 'int', 'bool', 'str', 'datetime', 'Category', 'Window'].includes(
        column.type.kind
    ) &&
    !column.name.startsWith('__');

const DataGrid: Widget = () => {
    const headerGrid = useRef<Grid>(null);
    const allColumns = useDataset(columnsSelector, shallow);

    const [scrollbarWidth] = getScrollbarSize();

    const defaultVisibleColumnKeys = useMemo(
        () =>
            allColumns
                .filter((column) => columnVisibleByDefault(column))
                .map(({ key }) => key),
        [allColumns]
    );

    const [tableView, setTableView] = useWidgetConfig<TableView>('tableView', 'full');
    const [visibleColumns, setVisibleColumns] = useWidgetConfig<string[]>(
        'visibleColumns',
        defaultVisibleColumnKeys
    );

    const resetVisibleColumns = useCallback(
        () => setVisibleColumns(defaultVisibleColumnKeys),
        [defaultVisibleColumnKeys, setVisibleColumns]
    );

    const [areOrderedByRelevance, setAreOrderedByRelevance] = useWidgetConfig(
        'orderByRelevance',
        false
    );

    const [sorting, setSorting] = useWidgetConfig<[string, Sorting][]>('sorting', []);

    const handleScroll = useCallback(
        ({ scrollLeft }: { scrollLeft: number }) =>
            headerGrid.current?.scrollTo({ scrollLeft, scrollTop: 0 }),
        []
    );

    return (
        <GridWrapper data-test-tag="datagrid">
            <TableViewProvider tableView={tableView} setTableView={setTableView}>
                <ColumnProvider
                    columnKeys={visibleColumns || []}
                    setColumnKeys={setVisibleColumns}
                    areOrderedByRelevance={areOrderedByRelevance}
                    setAreOrderedByRelevance={setAreOrderedByRelevance}
                    resetColumns={resetVisibleColumns}
                >
                    <SortingProvider sorting={sorting} setSorting={setSorting}>
                        <MenuBar />
                        <AutoSizerWrapper>
                            <AutoSizer>
                                {({ width, height }) => (
                                    <div tw="bg-white" style={{ width, height }}>
                                        <div tw="bg-gray-100 w-full">
                                            <HeaderGrid
                                                width={width - scrollbarWidth}
                                                height={headerHeight}
                                                ref={headerGrid}
                                            />
                                        </div>
                                        <TableGrid
                                            width={width}
                                            height={height - headerHeight}
                                            onScroll={handleScroll}
                                        />
                                    </div>
                                )}
                            </AutoSizer>
                        </AutoSizerWrapper>
                    </SortingProvider>
                </ColumnProvider>
            </TableViewProvider>
        </GridWrapper>
    );
};

DataGrid.defaultName = 'Table';
DataGrid.icon = TableIcon;
DataGrid.key = 'table';
DataGrid.legacyKeys = ['data-grid'];

export default DataGrid;

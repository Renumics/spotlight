import 'twin.macro';
import TableIcon from '../../icons/Table';
import { Widget } from '../types';
import { useCallback, useMemo, useRef } from 'react';
import AutoSizer from 'react-virtualized-auto-sizer';
import { VariableSizeGrid as Grid } from 'react-window';
import { Dataset, Sorting, useDataset } from '../../stores/dataset';
import { DataColumn, TableView } from '../../types';
import getScrollbarSize from '../../browser';
import { shallow } from 'zustand/shallow';
import useWidgetConfig from '../useWidgetConfig';
import { ColumnProvider } from './context/columnContext';
import { SortingProvider } from './context/sortingContext';
import { TableViewProvider } from './context/tableViewContext';
import HeaderGrid from './HeaderGrid';
import MenuBar from './MenuBar';
import TableGrid, { Ref as TableGridRef } from './TableGrid';
import GridContextMenu from './GridContextMenu';
import { WidgetContainer, WidgetContent } from '../../lib';
import { ColumnResizeProvider } from './context/resizeContext';

const headerHeight = 24;

const columnsSelector = (d: Dataset) => d.columns;

const columnVisibleByDefault = (column: DataColumn) =>
    ['float', 'int', 'bool', 'str', 'datetime', 'Category', 'Window'].includes(
        column.type.kind
    ) && !column.hidden;

const DataGrid: Widget = () => {
    const headerGrid = useRef<Grid>(null);
    const tableGrid = useRef<TableGridRef>(null);
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

    const resetGridsAfterIndex = useCallback((index: number) => {
        tableGrid.current?.resetAfterColumnIndex(index);
        headerGrid.current?.resetAfterColumnIndex(index);
    }, []);

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
        <WidgetContainer data-test-tag="datagrid">
            <TableViewProvider tableView={tableView} setTableView={setTableView}>
                <ColumnProvider
                    columnKeys={visibleColumns || []}
                    setColumnKeys={setVisibleColumns}
                    areOrderedByRelevance={areOrderedByRelevance}
                    setAreOrderedByRelevance={setAreOrderedByRelevance}
                    resetColumns={resetVisibleColumns}
                >
                    <ColumnResizeProvider onResize={resetGridsAfterIndex}>
                        <SortingProvider sorting={sorting} setSorting={setSorting}>
                            <MenuBar />
                            <WidgetContent>
                                <AutoSizer>
                                    {({ width, height }) => (
                                        <div tw="bg-white" style={{ width, height }}>
                                            <GridContextMenu>
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
                                                    ref={tableGrid}
                                                />
                                            </GridContextMenu>
                                        </div>
                                    )}
                                </AutoSizer>
                            </WidgetContent>
                        </SortingProvider>
                    </ColumnResizeProvider>
                </ColumnProvider>
            </TableViewProvider>
        </WidgetContainer>
    );
};

DataGrid.defaultName = 'Table';
DataGrid.icon = TableIcon;
DataGrid.key = 'table';
DataGrid.legacyKeys = ['data-grid'];

export default DataGrid;

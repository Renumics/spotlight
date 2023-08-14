import TableIcon from '../../icons/Table';
import { Widget } from '../types';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
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
import TableGrid, { Ref as TableGridRef } from './TableGrid';
import GridContextMenu from './GridContextMenu';
import columnWidthByType from './columnWidthByType';

const MIN_COLUMN_WIDTH = 50;

const headerHeight = 24;

const GridWrapper = tw.div`flex flex-col h-full w-full overflow-hidden`;
const AutoSizerWrapper = tw.div`flex-auto`;

const columnsSelector = (d: Dataset) => d.columns;

const columnVisibleByDefault = (column: DataColumn) =>
    ['float', 'int', 'bool', 'str', 'datetime', 'Category', 'Window'].includes(
        column.type.kind
    ) && !column.name.startsWith('__');

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
    const [columnWidths, persistColumnWidths] = useWidgetConfig<Record<string, number>>(
        'columnWidths',
        allColumns.reduce((acc: Record<string, number>, column: DataColumn) => {
            acc[column.key] = columnWidthByType[column.type.kind];
            return acc;
        }, {} as Record<string, number>)
    );

    const columnWidthsRef = useRef(columnWidths);

    useEffect(() => {
        columnWidthsRef.current = columnWidths;
    }, [columnWidths]);

    const resetGridsAfterIndex = useCallback((index: number) => {
        tableGrid.current?.resetAfterColumnIndex(index);
        headerGrid.current?.resetAfterColumnIndex(index);
    }, []);

    const [resizedIndex, setResizedIndex] = useState<number>();
    const lastResizePosition = useRef<number | null>(null);

    const onStartResize = useCallback(
        (columnIndex: number) => {
            const columnKey = visibleColumns[columnIndex];
            const onMouseMoveWhileResize = (event: MouseEvent) => {
                if (lastResizePosition.current !== null) {
                    const delta = event.clientX - lastResizePosition.current;
                    if (delta > 0 || delta < 0) {
                        const oldWidths = columnWidthsRef.current;
                        const newColumnWidth = Math.max(
                            MIN_COLUMN_WIDTH,
                            oldWidths[columnKey] + delta
                        );
                        const newWidths = {
                            ...oldWidths,
                            [columnKey]: newColumnWidth,
                        };
                        columnWidthsRef.current = newWidths;
                        resetGridsAfterIndex(columnIndex);
                    }
                } else {
                    setResizedIndex(columnIndex);
                }
                lastResizePosition.current = event.clientX;
            };

            window.addEventListener('mousemove', onMouseMoveWhileResize);

            const onMouseUpWhileResize = () => {
                window.removeEventListener('mousemove', onMouseMoveWhileResize);
                window.removeEventListener('mouseup', onMouseUpWhileResize);
                lastResizePosition.current = null;
                setResizedIndex(undefined);
                persistColumnWidths(columnWidthsRef.current);
            };

            window.addEventListener('mouseup', onMouseUpWhileResize);
        },
        [visibleColumns, resetGridsAfterIndex, persistColumnWidths]
    );

    const columnWidth = useCallback(
        (index: number) => columnWidthsRef.current[visibleColumns[index]],
        [visibleColumns]
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
                                        <GridContextMenu>
                                            <div tw="bg-gray-100 w-full">
                                                <HeaderGrid
                                                    width={width - scrollbarWidth}
                                                    height={headerHeight}
                                                    ref={headerGrid}
                                                    columnWidth={columnWidth}
                                                    onStartResize={onStartResize}
                                                    resizedIndex={resizedIndex}
                                                />
                                            </div>
                                            <TableGrid
                                                width={width}
                                                height={height - headerHeight}
                                                onScroll={handleScroll}
                                                columnWidth={columnWidth}
                                                ref={tableGrid}
                                            />
                                        </GridContextMenu>
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

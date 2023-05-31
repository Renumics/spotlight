import usePrevious from '../../hooks/usePrevious';
import { FunctionComponent, useCallback, useEffect, useRef } from 'react';
import { VariableSizeGrid as Grid } from 'react-window';
import type { GridOnScrollProps, GridProps } from 'react-window';
import Cell from './Cell';
import CellPlaceholder from './Cell/CellPlaceholder';
import {
    useColumnCount,
    useColumnWidth,
    useVisibleColumns,
} from './context/columnContext';
import getRowHeight from './getRowHeight';
import GridContextMenu from './GridContextMenu';
import useHighlight from './hooks/useHighlight';
import useRowCount from './hooks/useRowCount';
import useSort from './hooks/useSort';
import KeyboardControls from './KeyboardControls';
import MouseControls from './MouseControls';

interface Props {
    width: number;
    height: number;
    onScroll: GridProps['onScroll'];
}

const TableGrid: FunctionComponent<Props> = ({ width, height, onScroll }) => {
    const ref = useRef<Grid>(null);

    const columnWidth = useColumnWidth();

    const columnCount = useColumnCount();

    const [displayedColumns] = useVisibleColumns();

    const { getOriginalIndex } = useSort();
    const rowCount = useRowCount();

    const previousColumnKeys = usePrevious(displayedColumns.map(({ key }) => key));

    useEffect(() => {
        // find first changed Index
        const index =
            previousColumnKeys?.findIndex(
                (key, index) => displayedColumns[index]?.key !== key
            ) || 0;
        if (index >= 0) {
            ref?.current?.resetAfterColumnIndex(index);
        }
    }, [displayedColumns, previousColumnKeys]);

    const itemKey = useCallback(
        ({ columnIndex, rowIndex }: { columnIndex: number; rowIndex: number }) =>
            `${displayedColumns[columnIndex].key}/${getOriginalIndex(rowIndex)}`,
        [displayedColumns, getOriginalIndex]
    );

    const scrollToRow = useCallback((rowIndex: number) => {
        ref.current?.scrollToItem({ rowIndex });
    }, []);

    const updateHighlight = useHighlight(ref);

    const handleScroll = useCallback(
        (params: GridOnScrollProps) => {
            onScroll?.(params);
            updateHighlight();
        },
        [onScroll, updateHighlight]
    );

    // when the number of displayed rows or columns changes
    // new rows might not be correctly highlighted
    // so we update the highlights on any width or height change
    useEffect(updateHighlight, [width, height, updateHighlight]);

    return (
        <KeyboardControls scrollToRow={scrollToRow}>
            <MouseControls>
                <Grid
                    style={{ overflowY: 'scroll' }}
                    width={width}
                    height={height}
                    columnCount={columnCount}
                    rowCount={Math.max(1, rowCount)}
                    columnWidth={columnWidth}
                    estimatedColumnWidth={100}
                    rowHeight={getRowHeight}
                    itemKey={rowCount ? itemKey : undefined}
                    estimatedRowHeight={24}
                    overscanColumnCount={2}
                    overscanRowCount={8}
                    onScroll={handleScroll}
                    ref={ref}
                >
                    {rowCount ? Cell : CellPlaceholder}
                </Grid>
            </MouseControls>
        </KeyboardControls>
    );
};

export default TableGrid;

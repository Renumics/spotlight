import usePrevious from '../../hooks/usePrevious';
import {
    forwardRef,
    ForwardRefRenderFunction,
    useCallback,
    useContext,
    useEffect,
    useImperativeHandle,
    useRef,
} from 'react';
import type { GridOnScrollProps, GridProps } from 'react-window';
import { VariableSizeGrid as Grid } from 'react-window';
import Cell from './Cell';
import CellPlaceholder from './Cell/CellPlaceholder';
import { useColumnCount, useVisibleColumns } from './context/columnContext';
import getRowHeight from './getRowHeight';
import useHighlight from './hooks/useHighlight';
import useRowCount from './hooks/useRowCount';
import useSort from './hooks/useSort';
import KeyboardControls from './KeyboardControls';
import MouseControls from './MouseControls';
import { ResizingContext } from './context/resizeContext';

interface Props {
    width: number;
    height: number;
    onScroll: GridProps['onScroll'];
}

export type Ref = {
    resetAfterColumnIndex: (index: number) => void;
};

const TableGrid: ForwardRefRenderFunction<Ref, Props> = (
    { width, height, onScroll },
    fwdRef
) => {
    const ref = useRef<Grid>(null);

    useImperativeHandle(fwdRef, () => ({
        resetAfterColumnIndex: (index: number) => {
            ref.current?.resetAfterColumnIndex(index);
        },
    }));

    const columnCount = useColumnCount();

    const [displayedColumns] = useVisibleColumns();

    const { getColumnWidth } = useContext(ResizingContext);

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
                    columnWidth={getColumnWidth}
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

export default forwardRef(TableGrid);

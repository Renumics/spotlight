import {
    forwardRef,
    ForwardRefRenderFunction,
    useContext,
    useImperativeHandle,
    useRef,
} from 'react';
import { VariableSizeGrid } from 'react-window';
import type { GridOnScrollProps } from 'react-window';
import { IndexArray } from '../../types';
import DetailCell from './DetailCell';
import { RowHeightContext } from './rowHeightContext';
import { ViewConfig } from './types';

type ViewGridProps = {
    height: number;
    width: number;
    columnWidth: () => number;
    estimatedColumnWidth: number;
    views: ViewConfig[];
    rowIndices: IndexArray;
    onScroll: ({
        scrollUpdateWasRequested,
        scrollLeft,
        scrollTop,
    }: GridOnScrollProps) => void;
};

export type Ref = {
    scrollTo: ({
        scrollLeft,
        scrollTop,
    }: {
        scrollLeft?: number | undefined;
        scrollTop?: number | undefined;
    }) => void;
    resetAfterRowIndex: (index: number) => void;
    resetAfterColumnIndex: (index: number) => void;
};

const ViewGrid: ForwardRefRenderFunction<Ref, ViewGridProps> = (
    { height, width, columnWidth, estimatedColumnWidth, views, rowIndices, onScroll },
    ref
) => {
    const gridRef = useRef<VariableSizeGrid>(null);

    const { rowHeight } = useContext(RowHeightContext);

    useImperativeHandle(
        ref,
        () => ({
            scrollTo: ({ scrollLeft, scrollTop }) => {
                gridRef.current?.scrollTo({ scrollLeft, scrollTop });
            },
            resetAfterRowIndex: (index: number) => {
                gridRef.current?.resetAfterRowIndex(index);
            },
            resetAfterColumnIndex: (index: number) => {
                gridRef.current?.resetAfterColumnIndex(index);
            },
        }),
        []
    );

    return (
        <VariableSizeGrid
            ref={gridRef}
            height={height}
            width={width}
            columnWidth={columnWidth}
            estimatedColumnWidth={estimatedColumnWidth}
            itemKey={({ columnIndex, rowIndex }) =>
                `${views[rowIndex].key}/${rowIndices[columnIndex]}`
            }
            rowHeight={rowHeight}
            columnCount={rowIndices.length}
            rowCount={views.length}
            useIsScrolling={true}
            onScroll={onScroll}
            style={{ overflow: 'scroll' }}
        >
            {DetailCell}
        </VariableSizeGrid>
    );
};

export default forwardRef(ViewGrid);

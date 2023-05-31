import _ from 'lodash';
import * as React from 'react';
import {
    forwardRef,
    useCallback,
    useContext,
    useEffect,
    useImperativeHandle,
    useRef,
} from 'react';
import { Droppable, DragDropContext } from 'react-beautiful-dnd';
import type {
    DraggableProvided,
    DraggableRubric,
    DraggableStateSnapshot,
    DroppableProvided,
    DropResult,
} from 'react-beautiful-dnd';
import { VariableSizeList } from 'react-window';
import type { ListOnScrollProps } from 'react-window';
import { styled } from 'twin.macro';
import getScrollbarSize from '../../../browser';
import { RowHeightContext } from '../rowHeightContext';
import { State as StoreState, useStore } from '../store';
import Row, { DroppableRowItem as RowItem } from './Row';

const SCROLL_BORDER_OFFSET = 15;

const StyledList = styled(VariableSizeList)`
    &::-webkit-scrollbar {
        display: none;
    }
    --ms-overflow-style: none;
    scrollbar-width: none;
    overflow-y: scroll;
    overflow-x: scroll;
`;

type Props = {
    height: number;
    width: number;
    itemCount: number;
    onScroll: (props: ListOnScrollProps) => void;
};

export type Ref = {
    scrollTo: (scrollTo: number) => void;
    scrollToItemBottom: (index: number) => void;
    resetAfterIndex: (index: number) => void;
};

const moveViewsSelector = (state: StoreState) => state.moveView;

const renderClone = (
    provided: DraggableProvided,
    _snapshot: DraggableStateSnapshot,
    rubric: DraggableRubric
) => (
    <RowItem
        style={{ margin: 0 }}
        index={rubric.source.index}
        provided={provided}
        isDropped={true}
    />
);
const Header: React.ForwardRefRenderFunction<Ref, Props> = (
    { height, width, itemCount, onScroll },
    ref
) => {
    const moveView = useStore(moveViewsSelector);
    const { rowHeight } = useContext(RowHeightContext);
    const rowHeights = useRef<number[]>([]);

    useEffect(() => {
        rowHeights.current = Array(itemCount)
            .fill(1)
            .map((_, i) => rowHeight(i));
    }, [rowHeight, itemCount]);

    const detailsList = useRef<VariableSizeList>(null);

    const [, scrollbarHeight] = getScrollbarSize();

    useImperativeHandle(
        ref,
        () => ({
            scrollTo: (scrollTo: number) => {
                detailsList.current?.scrollTo(scrollTo);
            },
            scrollToItemBottom: (index: number) => {
                const listHeight = height - scrollbarHeight;

                const scrollOffset =
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    (detailsList.current?.state as any).scrollOffset || 0;

                const newScrollOffset =
                    _.sum(rowHeights.current.slice(0, index + 1)) - listHeight;

                if (scrollOffset < newScrollOffset + SCROLL_BORDER_OFFSET)
                    detailsList.current?.scrollTo(
                        newScrollOffset + SCROLL_BORDER_OFFSET
                    );
                else if (
                    scrollOffset >
                    newScrollOffset + (listHeight - SCROLL_BORDER_OFFSET)
                )
                    detailsList.current?.scrollTo(
                        newScrollOffset + listHeight - SCROLL_BORDER_OFFSET
                    );
            },
            resetAfterIndex: (index: number) => {
                detailsList.current?.resetAfterIndex(Math.floor(index / 2));
            },
        }),
        [height, scrollbarHeight]
    );

    const headerRowHeight = useCallback(
        (index: number) => (index % 2 === 0 ? rowHeight(Math.floor(index / 2)) : 0),
        [rowHeight]
    );

    const onDragEnd = useCallback(
        (result: DropResult) => {
            const sourceIndex = result.source.index;
            const destinationIndex = result.destination?.index;
            if (destinationIndex === undefined) return;
            moveView(sourceIndex, destinationIndex);
        },
        [moveView]
    );

    return (
        <DragDropContext onDragEnd={onDragEnd}>
            <Droppable
                droppableId="droppableDetailsList"
                mode="virtual"
                renderClone={renderClone}
            >
                {(droppableProvided: DroppableProvided) => {
                    return (
                        <StyledList
                            ref={detailsList}
                            height={height - scrollbarHeight}
                            itemCount={itemCount * 2}
                            itemSize={headerRowHeight}
                            width={width}
                            onScroll={onScroll}
                            outerRef={droppableProvided.innerRef}
                        >
                            {Row}
                        </StyledList>
                    );
                }}
            </Droppable>
        </DragDropContext>
    );
};

export default forwardRef(Header);

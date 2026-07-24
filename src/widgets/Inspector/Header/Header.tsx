import { DragDropProvider, DragOverlay } from '@dnd-kit/react';
import type { DragEndEvent } from '@dnd-kit/react';
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
import { VariableSizeList } from 'react-window';
import type { ListOnScrollProps } from 'react-window';
import { styled } from 'twin.macro';
import getScrollbarSize from '../../../browser';
import { RowHeightContext } from '../rowHeightContext';
import { State as StoreState, useStore } from '../store';
import Row, { RowItem } from './Row';

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

const moveViewsSelector = (state: StoreState) => state.moveLens;
const lensesSelector = (state: StoreState) => state.lenses;

const Header: React.ForwardRefRenderFunction<Ref, Props> = (
    { height, width, itemCount, onScroll },
    ref
) => {
    const moveView = useStore(moveViewsSelector);
    const lenses = useStore(lensesSelector);
    const { rowHeight } = useContext(RowHeightContext);
    const rowHeights = useRef<number[]>([]);
    const lensKeys = lenses.map(({ key }) => key);

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
        (event: DragEndEvent) => {
            const { source, target } = event.operation;
            if (event.canceled || !source || !target || source.id === target.id) return;

            const sourceIndex = lensKeys.indexOf(String(source.id));
            const destinationIndex = lensKeys.indexOf(String(target.id));
            if (sourceIndex === -1 || destinationIndex === -1) return;

            moveView(sourceIndex, destinationIndex);
        },
        [lensKeys, moveView]
    );

    return (
        <DragDropProvider onDragEnd={onDragEnd}>
            <StyledList
                ref={detailsList}
                height={height - scrollbarHeight}
                itemCount={itemCount * 2}
                itemSize={headerRowHeight}
                width={width}
                onScroll={onScroll}
            >
                {Row}
            </StyledList>
            <DragOverlay tw="shadow pointer-events-none">
                {(source) => {
                    const index = lensKeys.indexOf(String(source.id));
                    return index === -1 ? null : (
                        <RowItem
                            index={index}
                            style={{
                                height: rowHeights.current[index],
                                margin: 0,
                                width,
                            }}
                            isOverlay={true}
                        />
                    );
                }}
            </DragOverlay>
        </DragDropProvider>
    );
};

export default forwardRef(Header);

import {
    FunctionComponent,
    KeyboardEvent,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useRef,
} from 'react';
import { VariableSizeGrid } from 'react-window';
import type { GridOnScrollProps, ListOnScrollProps } from 'react-window';
import { Dataset, useDataset } from '../../stores/dataset';
import tw from 'twin.macro';
import getScrollbarSize from '../../browser';
import { DataContext } from './dataContext';
import Header, { Ref as HeaderRef } from './Header';
import RowHeightContext from './rowHeightContext';
import { State as StoreState, useStore } from './store';
import ViewGrid from './ViewGrid';
import Info from '../../components/ui/Info';

export const MIN_COLUMN_WIDTH = 128;
export const COLUMN_COUNT_OPTIONS = [1, 2, 4, 6, 8];

const HEADER_WIDTH = 24;

const DetailsGridWrapper = tw.div`flex`;

const viewsSelector = (state: StoreState) => state.views;
const focusedRowSelector = (d: Dataset) => d.lastFocusedRow;
const rowCountSelector = (d: Dataset) => d.length;

const DetailsGrid: FunctionComponent<{
    width: number;
    height: number;
    visibleColumnsCount: number;
}> = ({ width, height, visibleColumnsCount }) => {
    const [scrollbarWidth] = getScrollbarSize();
    const detailsGrid = useRef<VariableSizeGrid>(null);
    const header = useRef<HeaderRef>(null);
    const { rowIndices } = useContext(DataContext);
    const scrollLeft = useRef<number>();
    const scrollTop = useRef<number>();
    const mouseDown = useRef(false);
    const scrollTimer = useRef<ReturnType<typeof setTimeout>>();
    const leftItemIndex = useRef<number>(0);

    const views = useStore(viewsSelector);
    const focusedRow = useDataset(focusedRowSelector);
    const rowCount = useDataset(rowCountSelector);

    const [columnCount, columnWidth] = useMemo(() => {
        let visibleCount: number = visibleColumnsCount;
        const gridWidth = width - HEADER_WIDTH - scrollbarWidth;
        let newWidth = gridWidth / visibleColumnsCount;
        // snap to next lower column count in the available options in order to keep min column width
        while (newWidth < MIN_COLUMN_WIDTH && visibleCount > COLUMN_COUNT_OPTIONS[0]) {
            visibleCount =
                COLUMN_COUNT_OPTIONS[COLUMN_COUNT_OPTIONS.indexOf(visibleCount) - 1];
            newWidth = gridWidth / visibleCount;
        }
        return [visibleCount, newWidth];
    }, [visibleColumnsCount, width, scrollbarWidth]);

    const getColumnWidth = useCallback(() => columnWidth, [columnWidth]);

    useEffect(() => {
        detailsGrid.current?.resetAfterRowIndex(0);
        header.current?.resetAfterIndex(0);
    }, [views]);
    useEffect(() => detailsGrid.current?.resetAfterColumnIndex(0), [columnWidth]);

    const snapToItem = useCallback(
        (itemToScrollTo: number) => {
            detailsGrid.current?.scrollTo({
                scrollLeft: itemToScrollTo * columnWidth,
                scrollTop: scrollTop.current || 0,
            });
            leftItemIndex.current = itemToScrollTo;
        },
        [columnWidth]
    );

    const snapToClosestItem = useCallback(() => {
        const itemToScrollTo = Math.round((scrollLeft.current || 0) / columnWidth);
        snapToItem(itemToScrollTo);
    }, [columnWidth, snapToItem]);

    useEffect(() => {
        // when column width changed compute new scroll left based on visible left item and new column width
        scrollLeft.current = leftItemIndex.current * columnWidth;
        snapToClosestItem();
    }, [columnWidth, snapToClosestItem]);

    useEffect(() => {
        // scroll to focused item on focus
        if (focusedRow !== undefined) {
            snapToItem(Math.min(focusedRow, rowCount - visibleColumnsCount));
        }
    }, [focusedRow, rowCount, snapToItem, visibleColumnsCount]);

    const onScrollSnap = useCallback((): void => {
        // when mouse is still pressed dont scroll now but save scroll position
        if (mouseDown.current === false) {
            if (scrollLeft.current !== undefined) {
                snapToClosestItem();
            }
        }
    }, [snapToClosestItem]);

    const onScroll = useCallback(
        ({
            scrollUpdateWasRequested,
            scrollLeft: scrollOffsetLeft,
            scrollTop: scrollOffsetTop,
        }: GridOnScrollProps) => {
            header.current?.scrollTo(scrollOffsetTop);

            if (scrollTimer.current !== undefined) {
                clearTimeout(scrollTimer.current);
            }

            scrollLeft.current = scrollOffsetLeft;
            scrollTop.current = scrollOffsetTop;

            if (!scrollUpdateWasRequested) {
                scrollTimer.current = setTimeout(onScrollSnap, 150);
            }
        },
        [onScrollSnap]
    );

    const onScrollHeader = useCallback(
        ({ scrollOffset, scrollUpdateWasRequested }: ListOnScrollProps) => {
            if (scrollUpdateWasRequested) return;
            detailsGrid.current?.scrollTo({
                scrollTop: scrollOffset,
                scrollLeft: scrollLeft.current || 0,
            });
        },
        []
    );

    const onMouseDown = useCallback(() => {
        mouseDown.current = true;
    }, []);
    const onMouseUp = useCallback(() => {
        mouseDown.current = false;
        if (scrollLeft.current !== undefined) {
            snapToClosestItem();
        }
    }, [snapToClosestItem]);

    const onResize = useCallback(
        (resizedViewKey?: string) => {
            const resizedIndex = views.findIndex(({ key }) => key === resizedViewKey);
            detailsGrid.current?.resetAfterRowIndex(Math.max(0, resizedIndex));
            header.current?.resetAfterIndex(Math.max(0, resizedIndex));
            header.current?.scrollToItemBottom(resizedIndex);
        },
        [views]
    );

    const handleKeyDown = useCallback(
        (e: KeyboardEvent<HTMLDivElement>) => {
            const lastSelectedIndex = leftItemIndex.current;

            const step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;

            const nextSelectedIndex = Math.min(
                rowIndices.length - columnCount,
                Math.max(0, lastSelectedIndex + step)
            );

            if (nextSelectedIndex !== lastSelectedIndex) {
                detailsGrid.current?.scrollTo({
                    scrollLeft: nextSelectedIndex * columnWidth,
                });
                leftItemIndex.current = nextSelectedIndex;
            }
        },
        [rowIndices, columnCount, columnWidth]
    );

    return (
        <RowHeightContext onResize={onResize}>
            {/* eslint-disable-next-line jsx-a11y/no-static-element-interactions,jsx-a11y/no-noninteractive-tabindex */}
            <div tabIndex={0} onKeyDown={handleKeyDown} tw="focus:outline-none">
                <DetailsGridWrapper
                    style={{ width, height }}
                    onMouseDown={onMouseDown}
                    onMouseUp={onMouseUp}
                >
                    <Header
                        ref={header}
                        height={height}
                        width={HEADER_WIDTH}
                        itemCount={views.length}
                        onScroll={onScrollHeader}
                    />
                    {rowIndices.length > 0 && views.length > 0 ? (
                        <ViewGrid
                            ref={detailsGrid}
                            height={height}
                            width={width - HEADER_WIDTH}
                            columnWidth={getColumnWidth}
                            estimatedColumnWidth={columnWidth}
                            rowIndices={rowIndices}
                            views={views}
                            onScroll={onScroll}
                        />
                    ) : (
                        <Info>
                            {views.length === 0 ? (
                                <>No View Configured</>
                            ) : (
                                <>No Data Selected</>
                            )}
                        </Info>
                    )}
                </DetailsGridWrapper>
            </div>
        </RowHeightContext>
    );
};

export default DetailsGrid;

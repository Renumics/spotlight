import { MouseEvent, ReactNode, useCallback, useRef } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import { useTableView } from './context/tableViewContext';
import useSort from './hooks/useSort';

const highlightRowSelector = (d: Dataset) => ({
    highlightRowAt: d.highlightRowAt,
    dehighlightAll: d.dehighlightAll,
});
const selectRowsSelector = (d: Dataset) => d.selectRows;
const focusRowSelector = (d: Dataset) => d.focusRow;

interface Props {
    children?: ReactNode;
}

/**
 * Get the table row (in the current view) of an event target, -1 if the target
 * is not in a row, e.g. the grid itself or its scrollbar.
 */
const getRowIndex = (target: EventTarget): number => {
    const el = (target as HTMLElement).closest('div[data-rowindex]') as HTMLElement;
    return +(el?.dataset?.rowindex ?? -1);
};

const MouseControls = ({ children }: Props): JSX.Element => {
    const element = useRef<HTMLDivElement>(null);

    const { tableView } = useTableView();
    const { sortedIndices, getOriginalIndex, getSortedIndex } = useSort();

    const { highlightRowAt, dehighlightAll } = useDataset(highlightRowSelector);
    const selectRows = useDataset(selectRowsSelector);
    const focusRow = useDataset(focusRowSelector);

    const onHover = useCallback(
        (event: MouseEvent<HTMLElement>) => {
            const el = (event.target as HTMLElement).closest(
                'div[data-rowindex]'
            ) as HTMLElement;
            const rowIdx = +(el?.dataset?.rowindex || -1);
            if (rowIdx >= 0) highlightRowAt(getOriginalIndex(rowIdx), true);
            if (rowIdx < 0) dehighlightAll();
        },
        [dehighlightAll, highlightRowAt, getOriginalIndex]
    );

    const onLeave = useCallback(() => {
        dehighlightAll();
    }, [dehighlightAll]);

    // The row a mouse button was pressed on, -1 if there was none.
    const pressedRowIndex = useRef(-1);

    const onMouseDown = useCallback((event: MouseEvent<HTMLElement>) => {
        pressedRowIndex.current = getRowIndex(event.target);
    }, []);

    const onClick = useCallback(
        (event: MouseEvent<HTMLElement>) => {
            let rowIndex = getRowIndex(event.target);
            if (rowIndex < 0) {
                // The press and the release were in different cells, so the browser
                // dispatches the click to the grid around them, which is in no row.
                // The row that was pressed is the one meant.
                rowIndex = pressedRowIndex.current;
            }
            pressedRowIndex.current = -1;
            if (rowIndex < 0) return;

            const originalRowIndex = getOriginalIndex(rowIndex);
            if (originalRowIndex === undefined) return;

            const shiftKey = event.shiftKey;
            const ctrlKey = event.ctrlKey;

            const isIndexSelected = useDataset.getState().isIndexSelected;
            const isSelected = isIndexSelected[originalRowIndex];

            if (tableView !== 'selected') {
                if (!ctrlKey) {
                    if (!shiftKey) {
                        if (isSelected) {
                            selectRows(new Int32Array());
                        } else {
                            selectRows(Int32Array.of(originalRowIndex));
                        }
                    } else {
                        const selectedIndices = useDataset.getState().selectedIndices;

                        const lastPos = getSortedIndex(
                            selectedIndices[selectedIndices.length - 1]
                        );
                        const curPos = getSortedIndex(originalRowIndex);
                        const curPosOriginalIndex = getOriginalIndex(curPos);

                        if (lastPos < 0) {
                            if (curPos >= 0) {
                                selectRows(Int32Array.of(curPosOriginalIndex));
                            }
                            return;
                        }

                        const start = Math.min(lastPos, curPos);
                        const end = Math.max(lastPos, curPos);

                        const newIndices =
                            lastPos < curPos
                                ? sortedIndices.slice(start + 1, end + 1)
                                : sortedIndices.slice(start, end).reverse();

                        selectRows((selectedIndices) =>
                            Int32Array.of(...selectedIndices, ...newIndices)
                        );
                    }
                } else if (!shiftKey) {
                    if (isSelected) {
                        selectRows((selectedIndices) =>
                            selectedIndices.filter(
                                (index) => index !== originalRowIndex
                            )
                        );
                    } else {
                        selectRows((selectedIndices) =>
                            Int32Array.of(...selectedIndices, originalRowIndex)
                        );
                    }
                }
            } else {
                focusRow(rowIndex);
            }
        },
        [
            focusRow,
            selectRows,
            tableView,
            sortedIndices,
            getOriginalIndex,
            getSortedIndex,
        ]
    );

    return (
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
        <div
            ref={element}
            onMouseDown={onMouseDown}
            onClick={onClick}
            onMouseMove={onHover}
            onMouseLeave={onLeave}
        >
            {children}
        </div>
    );
};

export default MouseControls;

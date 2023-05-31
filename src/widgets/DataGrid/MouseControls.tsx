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

    const onClick = useCallback(
        (event: MouseEvent<HTMLElement>) => {
            const el = (event.target as HTMLElement).closest(
                'div[data-rowindex]'
            ) as HTMLElement;

            const rowIndex = +(el?.dataset?.rowindex ?? -1);

            const originalRowIndex = getOriginalIndex(rowIndex);

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
            onClick={onClick}
            onMouseMove={onHover}
            onMouseLeave={onLeave}
        >
            {children}
        </div>
    );
};

export default MouseControls;

import { KeyboardEvent, PropsWithChildren, useCallback, useRef } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import 'twin.macro';
import useSort from './hooks/useSort';

interface Props {
    scrollToRow: (index: number) => void;
}

const selectRowsSelector = (d: Dataset) => d.selectRows;

const KeyboardControls = ({
    scrollToRow,
    children,
}: PropsWithChildren<Props>): JSX.Element => {
    const selectRows = useDataset(selectRowsSelector);
    const { getSortedIndex, getOriginalIndex } = useSort();

    const containerRef = useRef<HTMLDivElement>(null);

    const handleKeyDown = useCallback(
        (e: KeyboardEvent<HTMLDivElement>) => {
            const selectedIndices = useDataset.getState().selectedIndices;
            const lastSelectedIndex = selectedIndices[selectedIndices.length - 1];
            if (lastSelectedIndex === undefined) return;

            const step = e.key === 'ArrowDown' ? 1 : e.key === 'ArrowUp' ? -1 : 0;

            if (step === 0) return;

            e.preventDefault();
            if (e.target != containerRef.current) {
                containerRef.current?.focus();
            }

            const sortedIndex = getSortedIndex(lastSelectedIndex);
            const nextSortedIndex = sortedIndex + step;
            const nextSelectedIndex = getOriginalIndex(nextSortedIndex);

            if (nextSelectedIndex !== undefined) {
                selectRows(Int32Array.of(nextSelectedIndex));
                scrollToRow(nextSortedIndex);
            }
        },
        [selectRows, scrollToRow, getOriginalIndex, getSortedIndex]
    );

    return (
        /* eslint-disable jsx-a11y/no-static-element-interactions,jsx-a11y/no-noninteractive-tabindex */
        <div
            tw="outline-none"
            tabIndex={0}
            ref={containerRef}
            onKeyDown={handleKeyDown}
        >
            {children}
        </div>
    );
};

export default KeyboardControls;

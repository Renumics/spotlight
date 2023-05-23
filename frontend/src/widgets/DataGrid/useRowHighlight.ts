import { useCallback } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';

const highlightRowSelector = (d: Dataset) => d.highlightRowAt;
const dehighlightRowSelector = (d: Dataset) => d.dehighlightRowAt;

interface ReturnType {
    isHighlighted: boolean;
    highlightRow: () => void;
    dehighlightRow: () => void;
}

function useRowHighlight(rowIndex: number): ReturnType {
    const isHighlightedSelector = useCallback(
        (d: Dataset) => d.isIndexHighlighted[rowIndex],
        [rowIndex]
    );
    const isHighlighted = useDataset(isHighlightedSelector);

    const highlightRowAt = useDataset(highlightRowSelector);
    const highlightRow = useCallback(
        () => highlightRowAt(rowIndex),
        [rowIndex, highlightRowAt]
    );

    const dehighlightRowAt = useDataset(dehighlightRowSelector);
    const dehighlightRow = useCallback(
        () => dehighlightRowAt(rowIndex),
        [rowIndex, dehighlightRowAt]
    );

    return { isHighlighted, highlightRow, dehighlightRow };
}

export default useRowHighlight;

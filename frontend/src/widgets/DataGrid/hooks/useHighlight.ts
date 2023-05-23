import { RefObject, useCallback, useEffect } from 'react';
import { VariableSizeGrid as Grid } from 'react-window';
import { useDataset } from '../../../stores/dataset';
import { theme } from 'twin.macro';
import { useTableView } from '../context/tableViewContext';
import useSort from './useSort';

function useHighlight(grid: RefObject<Grid>): () => void {
    const { tableView } = useTableView();
    const { getOriginalIndex } = useSort();

    const update = useCallback(() => {
        const dataset = useDataset.getState();
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const container = (grid.current as any)?._outerRef as
            | HTMLDivElement
            | undefined;

        if (!container) return;

        const cells = container.querySelectorAll<HTMLDivElement>('div[data-rowindex]');
        cells.forEach((cell) => {
            const gridRowIndex = parseInt(
                cell.getAttribute('data-rowindex') ?? '-1',
                10
            );
            const rowIndex = getOriginalIndex(gridRowIndex) ?? -1;

            const highlighted = dataset.isIndexHighlighted[rowIndex];
            const selected =
                tableView !== 'selected' && dataset.isIndexSelected[rowIndex];

            let bg = '';

            if (selected) {
                bg = highlighted ? theme`colors.blue.200` : theme`colors.blue.100`;
            } else {
                bg = highlighted ? theme`colors.gray.100` : '';
            }

            if (cell.style.backgroundColor !== bg) {
                cell.style.backgroundColor = bg;
            }
        });
    }, [grid, tableView, getOriginalIndex]);

    useEffect(() => useDataset.subscribe(update), [update]);

    return update;
}

export default useHighlight;

import { useRow } from '../hooks/useCell';
import { Problem } from '../types';

function useCellValues(
    rowIndex: number,
    columnKeys: string[],
    deferLoading = false
): [unknown[] | undefined, Problem | undefined] {
    const fetchDelay = deferLoading ? 200 : 0;
    const [values, problem] = useRow(rowIndex, columnKeys, fetchDelay);
    return [
        values === undefined ? values : columnKeys.map((key) => values[key]),
        problem,
    ];
}

export default useCellValues;

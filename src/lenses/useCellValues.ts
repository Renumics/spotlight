import { useRow } from '../hooks/useCell';

function useCellValues(rowIndex: number, columnKeys: string[], deferLoading = false) {
    const fetchDelay = deferLoading ? 200 : 0;
    const values = useRow(rowIndex, columnKeys, fetchDelay);
    return [
        values === undefined ? values : columnKeys.map((key) => values[key]),
        undefined,
    ];
}

export default useCellValues;

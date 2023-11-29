import { Dataset, useDataset } from '../../../stores/dataset';
import useSort from './useSort';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function useCellValue(columnKey: string, rowIndex: number): any {
    const originalIndex = useSort().getOriginalIndex(rowIndex);
    return useDataset((d: Dataset) => d.columnData[columnKey]?.[originalIndex]);
}

export default useCellValue;

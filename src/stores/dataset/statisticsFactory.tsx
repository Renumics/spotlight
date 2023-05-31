import { DataType, isNumerical } from '../../datatypes';
import { max, mean, min, quantile, standardDeviation } from 'simple-statistics';
import {
    ColumnData,
    ColumnsStats,
    DataColumn,
    DataStatistics,
    isNumberColumn,
} from '../../types';

export const makeStats = (
    type: DataType,
    data: ColumnData,
    mask?: boolean[]
): DataStatistics | undefined => {
    if (!isNumerical(type)) {
        return;
    }

    const numberValues = data.filter(
        (value, i) => (mask?.[i] ?? true) && !isNaN(value) && value !== null
    );
    if (numberValues.length === 0) {
        return;
    }
    return {
        min: min(numberValues as number[]),
        max: max(numberValues as number[]),
        mean: mean(numberValues as number[]),
        std: standardDeviation(numberValues as number[]),
        p5: quantile(numberValues as number[], 0.05),
        p95: quantile(numberValues as number[], 0.95),
    };
};

export const makeColumnsStats = (
    columns: DataColumn[],
    data: Record<string, ColumnData>,
    mask?: boolean[]
): ColumnsStats => {
    return columns
        .filter((column) => isNumberColumn(column))
        .reduce((a, column) => {
            const stats = makeStats(column.type, data[column.key], mask);
            if (stats !== undefined) {
                a[column.key] = stats;
            } else {
                delete a[column.key];
            }
            return a;
        }, {} as ColumnsStats);
};

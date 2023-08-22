import { useMemo } from 'react';
import { useDataset } from '../../lib';
import { isNumberColumn } from '../../types';
import { METRICS } from './metrics';
import { ValueArray } from './types';

export const useNumberColumnKeys = () => {
    const allColumns = useDataset((d) => d.columns);
    return useMemo(
        () => allColumns.filter(isNumberColumn).map((col) => col.key),
        [allColumns]
    );
};

export const useMetric = (metric?: string, columnKey?: string) => {
    const columnValues = useDataset((d) => (columnKey ? d.columnData[columnKey] : []));

    const filteredIndices = useDataset((d) => d.filteredIndices);
    const filteredValues = useMemo(
        () => filteredIndices.map((idx) => columnValues[idx]),
        [filteredIndices, columnValues]
    );
    const filteredMetric = useMemo(
        () =>
            metric !== undefined
                ? METRICS[metric].compute(filteredValues as ValueArray)
                : undefined,
        [metric, filteredValues]
    );

    const selectedIndices = useDataset((d) => d.selectedIndices);
    const selectedValues = useMemo(
        () => selectedIndices.map((idx) => columnValues[idx]),
        [selectedIndices, columnValues]
    );
    const selectedMetric = useMemo(
        () =>
            metric !== undefined && selectedValues.length > 0
                ? METRICS[metric].compute(selectedValues as ValueArray)
                : undefined,
        [metric, selectedValues]
    );

    return {
        filtered: filteredMetric,
        selected: selectedMetric,
    };
};

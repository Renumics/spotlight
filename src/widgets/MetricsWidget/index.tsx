import 'twin.macro';
import {
    Select,
    WidgetContainer,
    WidgetContent,
    WidgetMenu,
    dataformat,
    useDataset,
    useWidgetConfig,
} from '../../lib';
import { Widget } from '../types';
import { useMemo } from 'react';
import { isNumberColumn } from '../../types';
import _ from 'lodash';
import GaugeIcon from '../../icons/Gauge';

type ValueArray = number[] | Int32Array;

interface Metric {
    compute: (values: ValueArray) => number;
}

const METRICS: Record<string, Metric> = {
    sum: {
        compute: _.sum,
    },
    mean: {
        compute: _.mean,
    },
    min: {
        compute: (values) => _.min(values) ?? NaN,
    },
    max: {
        compute: (values) => _.max(values) ?? NaN,
    },
    count: {
        compute: (values) => values.length,
    },
};

const useNumberColumnKeys = () => {
    const allColumns = useDataset((d) => d.columns);
    return useMemo(
        () => allColumns.filter(isNumberColumn).map((col) => col.key),
        [allColumns]
    );
};

const useMetric = (metric?: string, columnKey?: string) => {
    if (metric === undefined || columnKey === undefined)
        return { filtered: undefined, selected: undefined };

    const columnValues = useDataset((d) => d.columnData[columnKey]);

    const filteredIndices = useDataset((d) => d.filteredIndices);
    const filteredValues = useMemo(
        () => filteredIndices.map((idx) => columnValues[idx]),
        [filteredIndices, columnValues]
    );
    const filteredMetric = useMemo(
        () => METRICS[metric].compute(filteredValues as ValueArray),
        [metric, filteredValues]
    );

    const selectedIndices = useDataset((d) => d.selectedIndices);
    const selectedValues = useMemo(
        () => selectedIndices.map((idx) => columnValues[idx]),
        [selectedIndices, columnValues]
    );
    const selectedMetric = useMemo(
        () =>
            selectedValues.length > 0
                ? METRICS[metric].compute(selectedValues as ValueArray)
                : undefined,
        [metric, selectedValues]
    );

    return {
        filtered: filteredMetric,
        selected: selectedMetric,
    };
};

const MetricsWidget: Widget = () => {
    const numberColumnKeys = useNumberColumnKeys();

    const [storedMetric, setStoredMetric] = useWidgetConfig<string>('metric');
    const [storedColumn, setStoredColumn] = useWidgetConfig<string>('column');

    const metric_keys = Object.keys(METRICS);
    const metric = storedMetric ?? metric_keys[0];
    const column =
        storedColumn && numberColumnKeys.includes(storedColumn)
            ? storedColumn
            : numberColumnKeys[0];

    const metricValues = useMetric(metric, column);

    return (
        <WidgetContainer>
            <WidgetMenu>
                <div tw="font-bold text-gray-700 px-1">f()</div>
                <div tw="w-32 h-full flex border-x border-gray-400">
                    <Select
                        options={metric_keys}
                        onChange={setStoredMetric}
                        value={metric}
                        variant="inset"
                    />
                </div>
                <div tw="font-bold text-gray-700 px-1">X</div>
                <div tw="w-32 h-full flex border-x border-gray-400">
                    <Select
                        options={numberColumnKeys}
                        onChange={setStoredColumn}
                        value={column}
                        variant="inset"
                    />
                </div>
            </WidgetMenu>
            <WidgetContent tw="flex items-center justify-center">
                <div tw="flex flex-col items-center">
                    <div tw="text-xl font-bold text-black">
                        {metricValues.filtered !== undefined
                            ? dataformat.formatNumber(metricValues.filtered)
                            : '-'}
                    </div>
                    <div tw="text-lg text-gray-800">
                        {metricValues.selected !== undefined
                            ? dataformat.formatNumber(metricValues.selected)
                            : '-'}
                    </div>
                </div>
            </WidgetContent>
        </WidgetContainer>
    );
};
MetricsWidget.key = 'Metric';
MetricsWidget.defaultName = 'Metric';
MetricsWidget.icon = GaugeIcon;

export default MetricsWidget;

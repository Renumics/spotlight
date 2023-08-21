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

interface Metric {
    compute: (values: number[]) => number;
}

const METRICS: Record<string, Metric> = {
    sum: {
        compute: _.sum,
    },
    mean: {
        compute: _.mean,
    },
};

const useNumberColumnKeys = () => {
    const allColumns = useDataset((d) => d.columns);
    return useMemo(
        () => allColumns.filter(isNumberColumn).map((col) => col.key),
        [allColumns]
    );
};

const useMetricValue = (metric?: string, columnKey?: string) => {
    if (metric === undefined || columnKey === undefined) return undefined;

    const columnValues = useDataset((d) => d.columnData[columnKey]);
    return useMemo(
        () => METRICS[metric].compute(columnValues as number[]),
        [metric, columnValues]
    );
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

    const metricValue = useMetricValue(metric, column);
    const metricValueText =
        metricValue !== undefined ? dataformat.formatNumber(metricValue) : '';

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
            <WidgetContent tw="flex items-center justify-center text-xl font-bold">
                {metricValueText}
            </WidgetContent>
        </WidgetContainer>
    );
};
MetricsWidget.key = 'Metric';
MetricsWidget.defaultName = 'Metric';
MetricsWidget.icon = () => <></>;

export default MetricsWidget;

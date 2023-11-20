import 'twin.macro';
import {
    Select,
    Tooltip,
    WidgetContainer,
    WidgetContent,
    WidgetMenu,
    useDataset,
    useDataformat,
    useWidgetConfig,
} from '../../lib';
import { Widget } from '../types';
import GaugeIcon from '../../icons/Gauge';
import { METRICS } from './metrics';
import { useMemo } from 'react';
import { ValueArray } from './types';

const useConfiguredMetric = () => {
    const [configuredMetric, setConfiguredMetric] = useWidgetConfig<string>('metric');
    const [configuredColumns, setConfiguredColumns] = useWidgetConfig<
        (string | undefined)[]
    >('columns', []);

    // Select metric by key from config.
    // Use default metric, if no metric is configured
    // or the configured metric doesn't exist.
    const metricKeys = Object.keys(METRICS);
    const metricKey =
        configuredMetric && metricKeys.includes(configuredMetric)
            ? configuredMetric
            : metricKeys[0];
    const metric = METRICS[metricKey];

    // Fetch valid columns for each param.
    const allColumns = useDataset((d) => d.columns);
    const validColumns = useMemo(() => {
        const validCols: Record<string, string[]> = {};
        Object.entries(metric.signature).forEach(([param, types]) => {
            validCols[param] = allColumns
                .filter((c) => types.includes(c.type.kind))
                .map((c) => c.key);
        });
        return validCols;
    }, [metric.signature, allColumns]);

    // Select columns by keys from config
    // Use first valid column, if no column is configured
    // or the configured column is invalid/missing.
    const columns = useMemo(() => {
        const cols: Record<string, string | undefined> = {};
        Object.entries(metric.signature).forEach(([param], i) => {
            const configColumn = configuredColumns[i] ?? '';
            cols[param] = validColumns[param].includes(configColumn)
                ? configColumn
                : validColumns[param][0];
        });
        return cols;
    }, [metric.signature, configuredColumns, validColumns]);

    // Finally calculate the selected metric over the
    // filtered and the selected rows.
    const columnData = useDataset((d) => d.columnData);
    const filteredRows = useDataset((d) => d.filteredIndices);
    const selectedRows = useDataset((d) => d.selectedIndices);

    const values = useMemo(() => {
        // skip calculation if metric is not fully configured
        if (
            Object.keys(metric.signature).some((param) => columns[param] === undefined)
        ) {
            return {
                filtered: undefined,
                selected: undefined,
            };
        }

        const filteredParamValues = Object.keys(metric.signature).map((param) => {
            const col = columns[param] ?? '';
            const data = new Array(filteredRows.length);
            for (let i = 0; i < filteredRows.length; i++) {
                data[i] = columnData[col][filteredRows[i]];
            }
            return data;
        });
        const selectedParamValues = Object.keys(metric.signature).map((param) => {
            const col = columns[param] ?? '';
            const data = new Array(selectedRows.length);
            for (let i = 0; i < selectedRows.length; i++) {
                data[i] = columnData[col][selectedRows[i]];
            }
            return data;
        });

        return {
            filtered: filteredRows.length
                ? metric.compute(filteredParamValues as ValueArray[])
                : undefined,
            selected: selectedRows.length
                ? metric.compute(selectedParamValues as ValueArray[])
                : undefined,
        };
    }, [metric, columns, columnData, filteredRows, selectedRows]);

    const setColumn = (param: string, column?: string) => {
        const paramIndex = Object.keys(metric.signature).indexOf(param);
        if (paramIndex === -1) return;
        setConfiguredColumns((prevColumns) => {
            const newColumns = prevColumns.slice();
            newColumns[paramIndex] = column;
            return newColumns;
        });
    };

    return {
        metricKey,
        signature: metric.signature,
        columns,
        validColumns,
        values,
        setMetricKey: setConfiguredMetric,
        setColumn,
    };
};

const MetricsWidget: Widget = () => {
    const {
        metricKey,
        signature,
        columns,
        validColumns,
        values,
        setMetricKey,
        setColumn,
    } = useConfiguredMetric();

    const formatter = useDataformat();

    return (
        <WidgetContainer>
            <WidgetMenu>
                <div tw="w-6 flex items-center justify-center font-bold text-gray-700 px-1">
                    <GaugeIcon />
                </div>
                <div tw="w-32 h-full flex border-x border-gray-400">
                    <Select
                        options={Object.keys(METRICS)}
                        onChange={setMetricKey}
                        value={metricKey}
                        variant="inset"
                    />
                </div>

                {Object.keys(signature).map((param: string) => (
                    <div tw="flex overflow-hidden" key={param}>
                        <div tw="font-bold text-gray-700 px-1">{param}</div>
                        <div tw="w-32 h-full flex border-x border-gray-400">
                            <Select
                                options={validColumns[param]}
                                onChange={(value) => setColumn(param, value)}
                                value={columns[param]}
                                variant="inset"
                            />
                        </div>
                    </div>
                ))}
            </WidgetMenu>
            <WidgetContent tw="flex items-center justify-center">
                <div tw="flex flex-col items-center">
                    <Tooltip content="all (filtered) rows">
                        <div tw="text-xl font-bold text-black">
                            {values.filtered !== undefined
                                ? formatter.formatFloat(values.filtered)
                                : '-'}
                        </div>
                    </Tooltip>
                    <Tooltip content="selected rows">
                        <div tw="text-lg text-gray-800">
                            {values.selected !== undefined
                                ? formatter.formatFloat(values.selected)
                                : '-'}
                        </div>
                    </Tooltip>
                </div>
            </WidgetContent>
        </WidgetContainer>
    );
};
MetricsWidget.key = 'Metric';
MetricsWidget.defaultName = 'Metric';
MetricsWidget.icon = GaugeIcon;

export default MetricsWidget;

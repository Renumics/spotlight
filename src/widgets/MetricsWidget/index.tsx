import 'twin.macro';
import {
    Select,
    WidgetContainer,
    WidgetContent,
    WidgetMenu,
    dataformat,
    useWidgetConfig,
} from '../../lib';
import { Widget } from '../types';
import GaugeIcon from '../../icons/Gauge';
import { METRICS } from './metrics';
import { useMetric, useNumberColumnKeys } from './hooks';

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

import { WidgetContainer, WidgetContent, WidgetMenu } from '../../lib';
import { Widget } from '../types';

const MetricsWidget: Widget = () => {
    return (
        <WidgetContainer>
            <WidgetMenu></WidgetMenu>
            <WidgetContent>Metric</WidgetContent>
        </WidgetContainer>
    );
};
MetricsWidget.key = 'Metric';
MetricsWidget.defaultName = 'Metric';
MetricsWidget.icon = () => <></>;

export default MetricsWidget;

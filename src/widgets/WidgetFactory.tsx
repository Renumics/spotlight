import * as React from 'react';
import { Dataset, useDataset } from '../stores/dataset';
import 'twin.macro';
import { Config } from './types';
import { WidgetContext } from './WidgetContext';
import { useComponentsStore } from '../stores/components';

interface Props {
    widgetType: string;
    widgetId: string;
    config: Record<string, unknown>;
    setConfig: React.Dispatch<React.SetStateAction<Config>>;
}

const datasetUidSelector = (d: Dataset) => d.uid;
const useDatasetUid = () => useDataset(datasetUidSelector);

const WidgetFactory = ({
    widgetType,
    widgetId,
    config,
    setConfig,
}: Props): JSX.Element => {
    const datasetUid = useDatasetUid();
    const widgetsByKey = useComponentsStore((state) => state.widgetsByKey);
    const WidgetComponent = widgetsByKey[widgetType];

    if (WidgetComponent) {
        const fullWidgetId = `widgets.${datasetUid}.${widgetType}.${widgetId}`;
        const context = {
            widgetId: fullWidgetId,
            config: config,
            setConfig: setConfig,
        };
        return (
            <WidgetContext.Provider value={context}>
                <WidgetComponent widgetId={fullWidgetId} />
            </WidgetContext.Provider>
        );
    }

    return (
        <div tw="w-full h-full flex justify-center items-center">
            <div tw="font-bold uppercase text-sm text-gray-700">{`Unknown Widget: ${widgetType}`}</div>
        </div>
    );
};

export default React.memo(WidgetFactory);

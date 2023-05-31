import * as React from 'react';
import { FunctionComponent } from 'react';
import { Dataset, useDataset } from '../stores/dataset';
import 'twin.macro';
import DataGrid from './DataGrid';
import Histogram from './Histogram';
import ScatterplotView from './ScatterplotView';
import Inspector from './Inspector';
import SimilarityMap from './SimilarityMap';
import { Config, Widget } from './types';
import { WidgetContext } from './WidgetContext';

interface Props {
    widgetType: string;
    widgetId: string;
    config: Record<string, unknown>;
    setConfig: React.Dispatch<React.SetStateAction<Config>>;
}

const datasetUidSelector = (d: Dataset) => d.uid;
const useDatasetUid = () => useDataset(datasetUidSelector);

export const widgets = [DataGrid, Inspector, SimilarityMap, ScatterplotView, Histogram];

export const widgetsById: Record<string, Widget> = {};
widgets.forEach((widget) => {
    widgetsById[widget.key] = widget;
    widget.legacyKeys?.forEach((key) => (widgetsById[key] = widget));
});

const WidgetFactory: FunctionComponent<Props> = ({
    widgetType,
    widgetId,
    config,
    setConfig,
}) => {
    const datasetUid = useDatasetUid();
    const WidgetComponent = widgetsById[widgetType];

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

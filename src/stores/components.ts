import _ from 'lodash';
import { create } from 'zustand';
import type { Widget } from '../widgets/types';
import type { Lens } from '../types';
import { DataType } from '../datatypes';
import { ALL_LENSES } from '../lenses';
import { ALL_WIDGETS } from '../widgets';

export function isLensCompatible<T>(
    view: Lens<T>,
    types: DataType[],
    canEdit: boolean
): boolean {
    return !!(
        types.length &&
        (canEdit || !view.isEditor) &&
        (types.length === 1 || view.multi) &&
        types.every((t) => view.dataTypes.includes(t.kind))
    );
}

export interface State {
    widgetsByKey: Record<string, Widget>;
    widgetKeys: string[];
    widgets: Widget[];
    lensesByKey: Record<string, Lens>;
    lensKeys: string[];
    lenses: Lens[];
}

export const useComponentsStore = create<State>(() => ({
    widgetsByKey: {},
    widgetKeys: [],
    widgets: [],
    lensesByKey: {},
    lensKeys: [],
    lenses: [],
}));

export function findCompatibleLenses(types: DataType[], canEdit: boolean) {
    return useComponentsStore
        .getState()
        .lensKeys.filter((lensKey) =>
            isLensCompatible(
                useComponentsStore.getState().lensesByKey[lensKey],
                types,
                canEdit
            )
        );
}

export function registerWidget(widget: Widget) {
    useComponentsStore.setState((state) => {
        const widgetsByKey = { ...state.widgetsByKey };
        [widget.key, ...(widget.legacyKeys ?? [])].forEach((key) => {
            widgetsByKey[key] = widget;
        });

        return {
            widgetsByKey,
            widgetKeys: Object.keys(widgetsByKey),
            widgets: _.uniq(Object.values(widgetsByKey)),
        };
    });
}
ALL_WIDGETS.forEach(registerWidget);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function registerLens(lens: Lens<any>) {
    useComponentsStore.setState((state) => {
        const lensesByKey = { ...state.lensesByKey, [lens.key]: lens };
        return {
            lensesByKey,
            lensKeys: Object.keys(lensesByKey),
            lenses: _.uniq(Object.values(lensesByKey)),
        };
    });
}
ALL_LENSES.forEach(registerLens);

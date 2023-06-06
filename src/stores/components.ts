import { create } from 'zustand';
import type { Widget } from '../widgets/types';
import type { Lens } from '../types';
import { DataType } from '../datatypes';
import { ALL_LENSES } from '../lenses';

export function isLensCompatible(
    view: Lens,
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
    lensesByKey: Record<string, Lens>;
    lensKeys: string[];
}

export const useComponentsStore = create<State>(() => ({
    widgetsByKey: {},
    widgetKeys: [],
    lensesByKey: {},
    lensKeys: [],
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
        const widgetsByKey = { ...state.widgetsByKey, [widget.key]: widget };
        return {
            widgetsByKey: widgetsByKey,
            widgetKeys: Object.keys(widgetsByKey),
        };
    });
}

export function registerLens(lens: Lens) {
    useComponentsStore.setState((state) => ({
        lensesByKey: { ...state.lensesByKey, [lens.key]: lens },
    }));
}
ALL_LENSES.forEach(registerLens);

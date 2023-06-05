import { create } from 'zustand';
import type { Widget } from '../widgets/types';
import type { Lens } from '../lenses/types';

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

export function registerWidget(widget: Widget) {
    useComponentsStore.setState((state) => ({
        widgetsByKey: { ...state.widgetsByKey, [widget.key]: widget },
    }));
}

export function registerLens(lens: Lens) {
    useComponentsStore.setState((state) => ({
        lensesByKey: { ...state.lensesByKey, [lens.key]: lens },
    }));
}

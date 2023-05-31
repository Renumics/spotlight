import {
    Dispatch,
    ReactNode,
    SetStateAction,
    createContext,
    useContext,
    useState,
    useMemo,
} from 'react';
import shortUUID from 'short-uuid';
import { createStore, useStore as useZustandStore, StoreApi } from 'zustand';
import { registry } from '../../lenses';
import { useDataset } from '../../lib';
import useWidgetConfig from '../useWidgetConfig';
import { ViewConfig } from './types';

export interface State {
    views: ViewConfig[];
    addView: (view: ViewConfig) => void;
    removeView: (view: ViewConfig) => void;
    moveView: (source: number, target: number) => void;
}

export const StoreContext = createContext<StoreApi<State> | null>(null);

const createInspectorStore = (
    initialViews: ViewConfig[],
    storeViews: Dispatch<SetStateAction<ViewConfig[]>>
) =>
    createStore<State>((set, get) => ({
        views: initialViews,
        addView: (view: ViewConfig) => {
            set((prev) => {
                const views = [...prev.views, view];
                storeViews(views);
                return { views };
            });
        },
        removeView: (view: ViewConfig) => {
            set((prev) => {
                const views = prev.views.filter((v) => v !== view);
                storeViews(views);
                return { views };
            });
        },
        moveView: (source: number, target: number) => {
            const newViews = get().views.slice();

            const draggedView = newViews[source];
            newViews.splice(source, 1);

            newViews.splice(target, 0, draggedView);

            set({ views: newViews });
        },
    }));

interface ProviderProps {
    children?: ReactNode;
}

const StoreProvider = ({ children }: ProviderProps): JSX.Element => {
    const autoViews = useMemo(() => {
        const richColumns = useDataset.getState().columns.filter((c) => c.lazy);
        const autoViews = richColumns.slice(0, 5).map((column) => {
            return {
                view: registry.findCompatibleViews([column.type], column.editable)[0],
                key: shortUUID.generate().toString(),
                name: column.name,
                columns: [column.key],
            };
        });
        return autoViews;
    }, []);

    const [storedViews, storeViews] = useWidgetConfig<ViewConfig[]>('views', autoViews);
    const [store] = useState(() => createInspectorStore(storedViews, storeViews));

    return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>;
};

function useStore<T>(selector: (state: State) => T) {
    const store = useContext(StoreContext);
    if (store == null) {
        throw new Error('Missing Inspector StoreProvider');
    }
    const value = useZustandStore(store, selector);
    return value;
}

export { useStore, StoreProvider };

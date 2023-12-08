import _ from 'lodash';
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
import { useDataset } from '../../stores/dataset';
import { isLensCompatible, useComponentsStore } from '../../stores/components';
import useWidgetConfig from '../useWidgetConfig';
import { LensConfig } from './types';

export interface State {
    lenses: LensConfig[];
    addLens: (view: LensConfig) => void;
    removeLens: (view: LensConfig) => void;
    moveLens: (source: number, target: number) => void;
    changeLens: (
        key: string,
        lens: LensConfig | ((prev: LensConfig) => LensConfig)
    ) => void;
}

export const StoreContext = createContext<StoreApi<State> | null>(null);

const createInspectorStore = (
    initialViews: LensConfig[],
    storeLenses: Dispatch<SetStateAction<LensConfig[]>>
) =>
    createStore<State>((set, get) => ({
        lenses: initialViews,
        addLens: (lens: LensConfig) => {
            set((prev) => {
                const lenses = [...prev.lenses, lens];
                storeLenses(lenses);
                return { lenses };
            });
        },
        removeLens: (lens: LensConfig) => {
            set((prev) => {
                const lenses = prev.lenses.filter((v) => v !== lens);
                storeLenses(lenses);
                return { lenses };
            });
        },
        moveLens: (source: number, target: number) => {
            const newLenses = get().lenses.slice();

            const draggedView = newLenses[source];
            newLenses.splice(source, 1);

            newLenses.splice(target, 0, draggedView);

            set({ lenses: newLenses });
        },
        changeLens: (key, lens) => {
            set((prev) => {
                const index = prev.lenses.findIndex((prevLens) => prevLens.key === key);

                if (typeof lens === 'function') {
                    lens = lens(prev.lenses[index]);
                }

                const lenses = prev.lenses.slice();
                lenses.splice(index, 1, lens);
                storeLenses(lenses);
                return {
                    lenses,
                };
            });
        },
    }));

interface ProviderProps {
    children?: ReactNode;
}

const StoreProvider = ({ children }: ProviderProps): JSX.Element => {
    const allColumns = useDataset((d) => d.columns);
    const lenses = useComponentsStore((d) => d.lensesByKey);
    const defaultLenses = useMemo(() => {
        const visibleColumns = allColumns.filter(
            (c) => !c.hidden && c.type.kind !== 'Embedding'
        );
        const binaryColumns = visibleColumns.filter((c) => c.type.binary);
        const defaultColumns = binaryColumns.length ? binaryColumns : visibleColumns;
        return _.compact(
            defaultColumns.map((column) => {
                const lens = Object.values(lenses).filter((lens) =>
                    isLensCompatible(lens, [column.type], column.editable)
                )[0];

                if (!lens) return;

                return {
                    view: lens.key,
                    key: shortUUID.generate().toString(),
                    name: column.name,
                    columns: [column.key],
                    settings: {},
                };
            })
        );
    }, [allColumns, lenses]);

    const [storedLenses, storeLenses] = useWidgetConfig<LensConfig[]>(
        'views',
        defaultLenses
    );
    const [store] = useState(() => createInspectorStore(storedLenses, storeLenses));

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

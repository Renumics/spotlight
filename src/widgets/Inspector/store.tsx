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
import { LensSpec } from '../../types';

export interface State {
    lenses: LensSpec[];
    addLens: (view: LensSpec) => void;
    removeLens: (view: LensSpec) => void;
    moveLens: (source: number, target: number) => void;
}

export const StoreContext = createContext<StoreApi<State> | null>(null);

const createInspectorStore = (
    initialLenses: LensSpec[],
    storeLenses: Dispatch<SetStateAction<LensSpec[]>>
) =>
    createStore<State>((set, get) => ({
        lenses: initialLenses,
        addLens: (lens: LensSpec) => {
            set((prev) => {
                const lenses = [...prev.lenses, lens];
                storeLenses(lenses);
                return { lenses };
            });
        },
        removeLens: (lens: LensSpec) => {
            set((prev) => {
                const lenses = prev.lenses.filter((v) => v !== lens);
                storeLenses(lenses);
                return { lenses };
            });
        },
        moveLens: (source: number, target: number) => {
            const newLenses = get().lenses.slice();
            const draggedLens = newLenses[source];
            newLenses.splice(source, 1);
            newLenses.splice(target, 0, draggedLens);
            set({ lenses: newLenses });
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

                const spec: LensSpec = {
                    kind: lens.kind,
                    key: shortUUID.generate().toString(),
                    name: column.name,
                    columns: [column.key],
                };
                return spec;
            })
        );
    }, [allColumns, lenses]);

    const [storedLenses, storeLenses] = useWidgetConfig<LensSpec[]>(
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

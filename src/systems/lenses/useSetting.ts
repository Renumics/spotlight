import localForage from 'localforage';
import { useCallback, useContext } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import LensContext from './LensContext';

interface SettingsStore {
    [key: string]: unknown;
}

export const useStore = create<SettingsStore>()(
    persist((set, get) => ({ set, get }), {
        name: 'dataview-settings-store',
        storage: createJSONStorage(localForage as never),
    })
);

const datasetIdSelector = (d: Dataset) => d.uid;

type Setter<T> = (value: T | ((previous: T) => T)) => void;

function useSetting<T>(name: string, defaultValue: T, global = false): [T, Setter<T>] {
    const { groupKey } = useContext(LensContext);
    const datasetId = useDataset(datasetIdSelector);

    const storageKey = global
        ? `${datasetId}.global.${name}`
        : `${datasetId}.${groupKey}.${name}`;

    const selector = useCallback(
        (state: SettingsStore) => state[storageKey],
        [storageKey]
    );
    const value = useStore(selector) ?? defaultValue;

    const setter: Setter<T> = useCallback(
        (value) =>
            useStore.setState((previousStage) => {
                const previousValue = previousStage[storageKey] ?? defaultValue;
                const newValue =
                    typeof value === 'function'
                        ? (value as CallableFunction)(previousValue)
                        : value;
                return { [storageKey]: newValue };
            }),
        [storageKey, defaultValue]
    );

    return [value as T, setter];
}

export default useSetting;

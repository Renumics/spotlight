import { useCallback, useContext } from 'react';
import LensContext from './LensContext';
import { Setter } from '../types';

function useSetting<T>(name: string, defaultValue: T): [T, Setter<T>] {
    const { settings, onChangeSettings } = useContext(LensContext);

    const setter: Setter<T> = useCallback(
        (value) => {
            if (typeof value === 'function') {
                onChangeSettings((previousSettings) => ({
                    [name]: (value as CallableFunction)(
                        previousSettings?.[name] ?? defaultValue
                    ),
                }));
            } else {
                onChangeSettings({ [name]: value });
            }
        },
        [name, defaultValue, onChangeSettings]
    );
    const value = settings?.[name] ?? defaultValue;

    return [value as T, setter];
}

export default useSetting;

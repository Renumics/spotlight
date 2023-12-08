import { useCallback, useContext } from 'react';
import LensContext from './LensContext';
import { Setter } from '../types';
import _ from 'lodash';

export function useSharedState<T = unknown>(
    key: string,
    defaultValue: T
): [T, Setter<T>] {
    const { sharedState, setSharedState } = useContext(LensContext);

    const setter: Setter<T> = useCallback(
        (valueOrCallback) => {
            setSharedState((state) => {
                const oldValue = (state[key] as T) ?? defaultValue;
                const newValue = _.isFunction(valueOrCallback)
                    ? valueOrCallback(oldValue)
                    : valueOrCallback;
                return { ...state, [key]: newValue };
            });
        },
        [key, defaultValue, setSharedState]
    );

    const value = (sharedState[key] as T) ?? defaultValue;

    return [value, setter];
}

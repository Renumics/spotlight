import _ from 'lodash';
import { useCallback, useEffect, useState } from 'react';
import configService from '../services/config';

export type ErrorHandler = (e?: Error) => void;
const defaultErrorHandler: ErrorHandler = (e?: Error) => {
    // eslint-disable-next-line no-console
    console.error(e);
};
export type StateSetter<T> = (
    value?: T | ((previousValue?: T) => T | undefined)
) => void;
export type ReturnType<T> = [T, StateSetter<T>, boolean];

function usePersistentState<T>(key: string): ReturnType<T | undefined>;
function usePersistentState<T>(key: string, initialValue: T): ReturnType<T>;
// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
function usePersistentState<T>(
    key: string,
    initialValue?: T,
    onError: ErrorHandler = defaultErrorHandler
) {
    const [storedValue, setStoredValue] = useState(initialValue);
    const [pending, setPending] = useState(true);

    useEffect(() => {
        let cancel = false;
        setPending(true);

        configService
            .get<T>(key)
            .then((value) => {
                if (cancel || value === null) return;
                setStoredValue(value);
                setPending(false);
            })
            .catch((e?: Error) => {
                onError(e);
            });

        return () => {
            cancel = true;
        };
    }, [key, onError]);

    const setValue: StateSetter<T> = useCallback(
        (value) => {
            if (_.isFunction(value)) {
                setStoredValue((previousValue) => {
                    const newValue = value(previousValue);
                    configService.set(key, newValue).catch(onError);
                    return newValue;
                });
            } else {
                setStoredValue(value);
                configService.set(key, value).catch(onError);
            }
        },
        [key, onError]
    );

    return [storedValue, setValue, pending] as const;
}

export default usePersistentState;

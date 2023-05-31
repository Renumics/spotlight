import _ from 'lodash';
import { useCallback, useEffect, useRef } from 'react';
import { Config } from './types';
import { useWidgetContext } from './WidgetContext';

type Setter<T> = React.Dispatch<React.SetStateAction<T>>;
type Return<T> = [T, Setter<T>];

function useWidgetConfig<T>(name: string): Return<T | undefined>;
function useWidgetConfig<T>(name: string, initialState: T): Return<T>;
// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
function useWidgetConfig<T>(name: string, initialState?: T) {
    const fallback = useRef(initialState);
    const { config, setConfig } = useWidgetContext();

    useEffect(() => {
        fallback.current = initialState;
    }, [initialState]);

    const storedValue = config[name];

    const setValue = useCallback(
        (newValue: T) => {
            setConfig((oldConfig: Config) => {
                const oldValue = oldConfig[name] ?? fallback.current;
                const value = _.isFunction(newValue) ? newValue(oldValue) : newValue;
                return { ...oldConfig, [name]: value };
            });
        },
        [name, setConfig]
    );

    return [storedValue ?? initialState, setValue];
}

export default useWidgetConfig;

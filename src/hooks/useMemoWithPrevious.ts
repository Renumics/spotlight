import { useMemo, useRef } from 'react';

function useMemoWithPrevious<T>(
    callback: (previous: T) => T,
    dependencies: unknown[],
    defaultValue: T
): T;
function useMemoWithPrevious<T>(
    callback: (previous?: T) => T,
    dependencies: unknown[],
    defaultValue?: T
): T {
    const valueRef = useRef<T | undefined>(defaultValue);
    const value = useMemo(
        () => callback(valueRef.current),
        [...dependencies] // eslint-disable-line react-hooks/exhaustive-deps
    );

    valueRef.current = value;

    return value;
}

export default useMemoWithPrevious;

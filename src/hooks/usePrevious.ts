import { useEffect, useRef } from 'react';

function usePrevious<T>(value: T): T | undefined {
    const valueRef = useRef<T>();

    const previousValue = valueRef.current;

    useEffect(() => {
        valueRef.current = value;
    }, [value]);

    return previousValue;
}

export default usePrevious;

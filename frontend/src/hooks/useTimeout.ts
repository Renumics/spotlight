import { useEffect, useRef } from 'react';

function useTimeout(callback: () => void, delay = 0): void {
    const latestCallback = useRef(callback);

    useEffect(() => (latestCallback.current = callback), [callback]);

    useEffect(() => {
        if (!delay) return;
        const timeout = setTimeout(() => latestCallback.current(), delay);
        return () => clearTimeout(timeout);
    }, [delay]);
}

export default useTimeout;

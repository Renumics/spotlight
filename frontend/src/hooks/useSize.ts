import useResizeObserver from '@react-hook/resize-observer';
import { RefObject, useLayoutEffect, useState } from 'react';

interface Size {
    width: number;
    height: number;
}

const useSize = (ref: RefObject<HTMLElement>): Size => {
    const [size, setSize] = useState<ClientRect>();

    useLayoutEffect(() => {
        const rect = ref.current?.getBoundingClientRect();
        setSize(rect);
    }, [ref]);

    useResizeObserver(ref, (element) => setSize(element.contentRect));
    return size || { width: 0, height: 0 };
};

export default useSize;

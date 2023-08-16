import useResizeObserver from '@react-hook/resize-observer';
import { RefObject, useLayoutEffect, useState } from 'react';

interface Size {
    width: number;
    height: number;
}

const useSize = (ref: RefObject<HTMLElement>): Size => {
    const [size, setSize] = useState<Size>({ width: 0, height: 0 });

    useLayoutEffect(() => {
        setSize({
            width: ref.current?.offsetWidth ?? 0,
            height: ref.current?.offsetHeight ?? 0,
        });
    }, [ref]);

    useResizeObserver(ref, (element) =>
        setSize({
            width: element.contentRect.width,
            height: element.contentRect.height,
        })
    );
    return size;
};

export default useSize;

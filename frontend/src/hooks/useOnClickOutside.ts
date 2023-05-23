import { MutableRefObject, useEffect } from 'react';

type ElementRef = MutableRefObject<HTMLElement | null>;
type Callback = (event: Event) => void;

function useOnClickOutside(ref: ElementRef, callback?: Callback): void {
    useEffect(() => {
        if (callback === undefined) return;

        const handleMousedown = (event: Event) => {
            const selectMenuRoot = document.getElementById('selectMenuRoot');
            const insideMenuRoot = selectMenuRoot?.contains(
                event.target as HTMLElement
            );

            const insideContainer = ref.current?.contains(event.target as HTMLElement);

            if (insideContainer || insideMenuRoot) return;
            callback(event);
        };

        document.addEventListener('mousedown', handleMousedown, true);

        return () => {
            document.removeEventListener('mousedown', handleMousedown, true);
        };
    }, [ref, callback]);
}

export default useOnClickOutside;

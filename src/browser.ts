import { Vec2 } from './types';

let scrollbarSize: Vec2 | undefined = undefined;

const getScrollbarSize = (): Vec2 => {
    if (scrollbarSize === undefined) {
        // Creating invisible container
        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.overflow = 'scroll'; // forcing scrollbar to appear
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (outer.style as any).msOverflowStyle = 'scrollbar'; // needed for WinJS apps
        document.body.appendChild(outer);

        // Creating inner element and placing it in the container
        const inner = document.createElement('div');
        outer.appendChild(inner);

        // Calculating difference between container's full width and the child width
        const scrollbarWidth = outer.offsetWidth - inner.offsetWidth;

        // Calculating difference between container's full width and the child width
        const scrollbarHeight = outer.offsetHeight - inner.offsetHeight;

        // Removing temporary elements from the DOM
        outer.parentNode?.removeChild(outer);
        scrollbarSize = [scrollbarWidth, scrollbarHeight];
    }

    return scrollbarSize;
};

export default getScrollbarSize;

import { registry } from '../../lenses';
import {
    createContext,
    FunctionComponent,
    ReactNode,
    useCallback,
    useEffect,
    useRef,
    useState,
} from 'react';
import { shallow } from 'zustand/shallow';
import { State, useStore } from './store';

type RowHeightContextState = {
    startResize: (index: number, screenY: number) => void;
    rowHeight: (index: number) => number;
};

export const RowHeightContext = createContext<RowHeightContextState>({
    startResize: () => null,
    rowHeight: () => 0,
});

type RowHeightProviderProps = {
    onResize?: (resizedView: string) => void;
    children?: ReactNode;
};

const viewsSelector = (state: State) => state.views;

let resizingLoopInterval: ReturnType<typeof setInterval> | undefined = undefined;

const RowHeightProvider: FunctionComponent<RowHeightProviderProps> = ({
    onResize = () => null,
    children,
}) => {
    const ref = useRef<HTMLDivElement>(null);
    const [rowHeights, setRowHeights] = useState<Record<string, number>>({});
    const [isResizing, setIsResizing] = useState(false);
    const resizedRow = useRef<string>();
    const startScreenY = useRef<number>(0);
    const lastScreenY = useRef<number>(0);
    const startHeight = useRef<number>(0);
    const currentHeight = useRef<number>(0);

    const views = useStore(viewsSelector);

    useEffect(() => {
        const newRowHeights = views.reduce((a, viewConfig) => {
            a[viewConfig.key] =
                rowHeights[viewConfig.key] ??
                registry.views[viewConfig.view]?.defaultHeight ??
                24;
            return a;
        }, {} as Record<string, number>);
        if (!shallow(newRowHeights, rowHeights)) {
            setRowHeights(newRowHeights);
        }
    }, [views, rowHeights]);

    const rowHeight = useCallback(
        (index: number) => rowHeights[views[index]?.key] ?? 24,
        [rowHeights, views]
    );

    const startResize = useCallback(
        (index: number, screenY: number) => {
            const viewKey = views[index].key;
            resizedRow.current = viewKey;
            startScreenY.current = screenY;
            lastScreenY.current = screenY;
            startHeight.current = rowHeights[viewKey];
            currentHeight.current = startHeight.current;
            setIsResizing(true);
        },
        [rowHeights, views]
    );

    const resizeView = useCallback(
        (rowKey: string, newHeight: number) => {
            const viewConfig = views.find(({ key }) => key === rowKey);
            if (viewConfig !== undefined) {
                const maxHeight = registry.views[viewConfig.view]?.maxHeight;
                if (maxHeight !== undefined) {
                    newHeight = Math.min(maxHeight, newHeight);
                }
                const minHeight = registry.views[viewConfig.view]?.minHeight || 12;
                if (minHeight !== undefined) {
                    newHeight = Math.max(minHeight, newHeight);
                }
            }
            currentHeight.current = newHeight;
            setRowHeights((rowHeights) => ({
                ...rowHeights,
                [rowKey]: currentHeight.current,
            }));
            onResize(rowKey);
        },
        [onResize, views]
    );

    const onMouseMove = useCallback(
        (event: React.MouseEvent<HTMLDivElement>) => {
            if (resizingLoopInterval !== undefined) clearInterval(resizingLoopInterval);

            const rowKey = resizedRow.current;

            if (!isResizing || rowKey === undefined) return;

            const rect = ref.current?.getBoundingClientRect();

            const relY = rect?.height
                ? (event.clientY - (rect?.top || 0)) / rect?.height
                : 0.5;

            if (relY > 0.9 && rect) {
                const scrollSpeed = (relY - 0.9) * 10;
                resizingLoopInterval = setInterval(() => {
                    resizeView(
                        rowKey,
                        currentHeight.current + Math.ceil(15 * scrollSpeed)
                    );
                }, 50);
                return;
            }

            if (relY < 0.1 && rect) {
                const scrollSpeed = (relY - 0.1) * -10;
                resizingLoopInterval = setInterval(() => {
                    resizeView(
                        rowKey,
                        currentHeight.current - Math.ceil(15 * scrollSpeed)
                    );
                }, 50);
                return;
            }

            const newHeight =
                currentHeight.current + event.screenY - lastScreenY.current;
            lastScreenY.current = event.screenY;
            resizeView(rowKey, newHeight);
        },
        [isResizing, resizeView]
    );

    const onMouseUp = useCallback(() => {
        if (isResizing) {
            setIsResizing(false);
            resizedRow?.current !== undefined && onResize?.(resizedRow.current);
            resizingLoopInterval !== undefined && clearInterval(resizingLoopInterval);
        }
    }, [isResizing, onResize]);

    const onMouseLeave = useCallback(() => {
        if (isResizing) {
            const rowKey = resizedRow.current;
            if (rowKey !== undefined && isResizing) {
                setRowHeights((rowHeights) => ({
                    ...rowHeights,
                    [rowKey]: startHeight.current,
                }));
            }
            setIsResizing(false);
            resizedRow?.current !== undefined && onResize?.(resizedRow.current);
            resizingLoopInterval !== undefined && clearInterval(resizingLoopInterval);
        }
    }, [isResizing, onResize]);

    return (
        <RowHeightContext.Provider value={{ startResize, rowHeight }}>
            {/* eslint-disable-next-line jsx-a11y/no-static-element-interactions */}
            <div
                ref={ref}
                onMouseMove={onMouseMove}
                onMouseLeave={onMouseLeave}
                onMouseUp={onMouseUp}
            >
                {children}
            </div>
        </RowHeightContext.Provider>
    );
};

export default RowHeightProvider;

import * as React from 'react';
import { MutableRefObject, useCallback, useMemo, useRef } from 'react';
import { useColumns } from './columnContext';
import columnWidthByType from '../columnWidthByType';
import { useWidgetConfig } from '../../../hooks';

const MIN_COLUMN_WIDTH = 50;

type EditingContextState = {
    getColumnWidth: (index: number) => number;
    startResizing: (columnIndex: number) => void;
    resizedIndex: MutableRefObject<number | undefined>;
};

export const ResizingContext = React.createContext<EditingContextState>({
    getColumnWidth: () => MIN_COLUMN_WIDTH,
    startResizing: () => undefined,
    resizedIndex: { current: undefined },
});

interface Props {
    children: React.ReactNode;
    onResize: (columnIndex: number) => void;
}

export const ColumnResizeProvider = ({ children, onResize }: Props) => {
    const columns = useColumns();

    const defaultColumnWidths = useMemo(
        () =>
            columns.reduce((acc, column) => {
                acc[column.key] = columnWidthByType[column.type.kind];
                return acc;
            }, {} as Record<string, number>),
        [columns]
    );

    const resizedIndex = useRef<number>();
    const lastResizePosition = useRef<number | null>(null);

    const [columnWidths, _persistColumnWidths] = useWidgetConfig<
        Record<string, number>
    >('dataGridColumnWidths', {});

    const columnWidthsRef = useRef<Record<string, number>>({});

    const persistColumnWidths = useCallback(() => {
        _persistColumnWidths((oldWidths) => ({
            ...oldWidths,
            ...columnWidthsRef.current,
        }));
    }, [_persistColumnWidths]);

    const onStartResize = useCallback(
        (columnIndex: number) => {
            const columnKey = columns[columnIndex].key;
            const onMouseMoveWhileResize = (event: MouseEvent) => {
                if (lastResizePosition.current !== null) {
                    const delta = event.clientX - lastResizePosition.current;
                    if (delta > 0 || delta < 0) {
                        const currentWidth =
                            columnWidthsRef.current[columnKey] ||
                            defaultColumnWidths[columnKey] ||
                            MIN_COLUMN_WIDTH;
                        columnWidthsRef.current[columnKey] = Math.max(
                            MIN_COLUMN_WIDTH,
                            currentWidth + delta
                        );
                        onResize(columnIndex);
                    }
                } else {
                    resizedIndex.current = columnIndex;
                }
                lastResizePosition.current = event.clientX;
            };

            window.addEventListener('mousemove', onMouseMoveWhileResize);

            const onMouseUpWhileResize = () => {
                window.removeEventListener('mousemove', onMouseMoveWhileResize);
                window.removeEventListener('mouseup', onMouseUpWhileResize);
                lastResizePosition.current = null;
                resizedIndex.current = undefined;
                persistColumnWidths();
            };

            window.addEventListener('mouseup', onMouseUpWhileResize);
        },
        [columns, defaultColumnWidths, onResize, persistColumnWidths]
    );

    const getColumnWidth = useCallback(
        (index: number) => {
            const columnKey = columns[index]?.key;
            if (columnKey) {
                return (
                    columnWidthsRef.current[columnKey] ||
                    columnWidths[columnKey] ||
                    defaultColumnWidths[columnKey] ||
                    MIN_COLUMN_WIDTH
                );
            }
            return 0;
        },
        [columnWidths, columns, defaultColumnWidths]
    );

    return (
        <ResizingContext.Provider
            value={{ getColumnWidth, startResizing: onStartResize, resizedIndex }}
        >
            {children}
        </ResizingContext.Provider>
    );
};

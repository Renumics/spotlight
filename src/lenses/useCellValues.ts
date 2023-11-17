import { useCallback, useEffect, useRef, useState } from 'react';
import { Dataset, useDataset } from '../stores/dataset';
import { Problem } from '../types';
import api from '../api';
import { shallow } from 'zustand/shallow';
import { usePrevious } from '../hooks';

async function fetchValue(row: number, column: string, raw: boolean) {
    const response = await api.table.getCellRaw({
        row,
        column,
        generationId: useDataset.getState().generationID,
    });
    if (raw) {
        return response.raw.arrayBuffer();
    } else {
        return response.value();
    }
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function useCellValues(
    rowIndex: number,
    columnKeys: string[],
    deferLoading = false
): [unknown[] | undefined, Problem | undefined] {
    const cellsSelector = useCallback(
        (d: Dataset) => {
            return columnKeys.map((key) => d.columnData[key][rowIndex]);
        },
        [rowIndex, columnKeys]
    );
    const columnsSelector = useCallback(
        (d: Dataset) => {
            return columnKeys.map((key) =>
                d.columns.find((column) => column.key === key)
            );
        },
        [columnKeys]
    );

    const cellEntries = useDataset(cellsSelector, shallow);
    const columns = useDataset(columnsSelector, shallow);
    const generationId = useDataset((d) => d.generationID);
    const previousGenerationId = usePrevious(generationId);

    const [values, setValues] = useState<unknown[] | undefined>();
    const [problem, setProblem] = useState<Problem>();

    // store all values in promises
    const promisesRef = useRef<Record<string, Promise<unknown>>>({});

    const cancelledRef = useRef<boolean>(false);
    useEffect(() => {
        // reset cancelled for StrictMode in dev
        cancelledRef.current = false;
        return () => {
            cancelledRef.current = true;
        };
    }, []);

    useEffect(() => {
        const promises = promisesRef.current;

        if (generationId !== previousGenerationId) {
            for (let i = 0; i < columns.length; i++) {
                const columnKey = columnKeys[i];
                const column = columns[i];

                if (!column) {
                    promises[columnKey] = Promise.resolve(null);
                } else if (!column.type.lazy) {
                    promises[columnKey] = Promise.resolve(cellEntries[i]);
                } else {
                    // only refresh lazy string columns (for now)
                    if (column.type.kind === 'str' || !promises[columnKey]) {
                        promises[columnKey] = delay(deferLoading ? 250 : 0).then(() => {
                            if (!cancelledRef.current)
                                return fetchValue(
                                    rowIndex,
                                    columnKeys[i],
                                    column.type.binary
                                );
                        });
                    }
                }
            }
            Promise.all(Object.values(promises))
                .then((values) => {
                    if (!cancelledRef.current) setValues(values);
                })
                .catch((error) => {
                    if (!cancelledRef.current) {
                        console.error(error);
                        setProblem(error);
                    }
                });
        }
    }, [
        cellEntries,
        columnKeys,
        columns,
        deferLoading,
        generationId,
        previousGenerationId,
        rowIndex,
    ]);

    return [values, problem];
}

export default useCellValues;

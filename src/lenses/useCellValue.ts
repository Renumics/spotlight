import { useCallback, useEffect, useMemo, useState } from 'react';
import { Dataset, useDataset } from '../stores/dataset';
import { Problem } from '../types';
import api from '../api';
import { shallow } from 'zustand/shallow';

async function fetchValue(row: number, column: string, raw: boolean = true) {
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

async function keepValue(value: unknown) {
    return value;
}

function useCellValues(
    rowIndex: number,
    columnKeys: string[]
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

    const needsFetch = useMemo(
        () => cellEntries.some((entry, i) => entry !== null && columns[i]?.lazy),
        [cellEntries, columns]
    );

    const [fetchedValues, setFetchedValues] = useState<unknown[] | undefined>();
    const [problem, setProblem] = useState<Problem>();
    const hasFetchedValues = !!fetchedValues;

    useEffect(() => {
        let cancelled = false;
        if (!needsFetch) return;

        // Keep previously fetched values for any lazy datatype
        if (hasFetchedValues) {
            setFetchedValues((previous) =>
                cellEntries.map((entry, i) =>
                    entry !== null && columns[i]?.lazy ? previous?.[i] : entry
                )
            );
            return;
        }

        const fetchers = cellEntries.map((entry, i) => {
            const column = columns[i];
            return entry !== null && column?.lazy
                ? fetchValue(
                      rowIndex,
                      columnKeys[i],
                      !['Embedding', 'Array'].includes(column.type.kind)
                  )
                : keepValue(entry);
        });

        Promise.all(fetchers)
            .then((values) => {
                if (!cancelled) setFetchedValues(values);
            })
            .catch((error) => {
                if (!cancelled) setProblem(error);
            });

        return () => {
            cancelled = true;
        };
    }, [cellEntries, rowIndex, columnKeys, needsFetch, columns, hasFetchedValues]);

    const values = needsFetch ? fetchedValues : cellEntries;

    return [values, problem];
}

export default useCellValues;

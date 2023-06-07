import { useCallback, useEffect, useMemo, useState } from 'react';
import { Dataset, useDataset } from '../stores/dataset';
import { Problem } from '../types';
import api from '../api';
import { shallow } from 'zustand/shallow';

async function fetchValue(row: number, column: string) {
    const response = await api.table.getCellRaw({
        row,
        column,
        generationId: useDataset.getState().generationID,
    });
    return response.raw.arrayBuffer();
}

async function keepValue(value: unknown) {
    return value;
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function useCellValues(
    rowIndex: number,
    columnKeys: string[],
    deferLoading?: boolean = false
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

        const fetchers = cellEntries.map((entry, i) =>
            entry !== null && columns[i]?.lazy
                ? delay(deferLoading ? 250 : 0).then(() => {
                      if (cancelled) {
                          console.log('canceled');
                      } else {
                          return fetchValue(rowIndex, columnKeys[i]);
                      }
                  })
                : keepValue(entry)
        );

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
    }, [
        cellEntries,
        rowIndex,
        columnKeys,
        needsFetch,
        columns,
        hasFetchedValues,
        deferLoading,
    ]);

    const values = needsFetch ? fetchedValues : cellEntries;

    return [values, problem];
}

export default useCellValues;

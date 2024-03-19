import { useEffect, useState } from 'react';
import api from '../api';
import { Dataset, useDataset } from '../stores/dataset';
import { Problem, isProblem } from '../types';
import { ApiResponse } from '../client';

interface CachedCell {
    generationId: number;
    promise: Promise<unknown>;
}
const cellCacheCapacity = 100;
const cellCache: Map<string, CachedCell> = new Map();

async function _sleep(ms: number) {
    await new Promise((resolve) => setTimeout(resolve, ms));
}

async function _fetchCell(
    column: string,
    row: number,
    generationId: number,
    asBuffer: boolean
) {
    const max_tries = 3;
    let tries = 0;
    let response: ApiResponse<unknown> | undefined = undefined;

    while (!response) {
        try {
            response = await api.table.getCellRaw({ column, row, generationId });
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: any) {
            const problem = await error.response.json?.();
            if (++tries > max_tries || problem?.type !== 'GenerationIDMismatch') {
                throw error;
            }
            await _sleep(100);
        }
    }

    if (asBuffer) {
        return response.raw.arrayBuffer();
    } else {
        return response.value();
    }
}

function _getCell(
    datasetId: string,
    column: string,
    row: number,
    generationId: number,
    asBuffer: boolean,
    fetchDelay = 0
) {
    const cacheKey = `${datasetId},${column},${row},${asBuffer}`;
    let cell = cellCache.get(cacheKey);
    if (cell?.generationId != generationId) {
        if (fetchDelay) _sleep(fetchDelay);
        const promise = _fetchCell(column, row, generationId, asBuffer);
        cell = {
            generationId,
            promise,
        };

        // remove oldest 10% if cache is full
        if (cellCache.size > cellCacheCapacity) {
            const keyIter = cellCache.keys();
            const removeCount = Math.ceil(cellCacheCapacity / 10);
            for (let i = 0; i < removeCount; i++) {
                cellCache.delete(keyIter.next().value);
            }
        }

        cellCache.set(cacheKey, cell);
    }
    return cell.promise;
}

function _errorToProblem(e: unknown): Problem {
    if (isProblem(e)) {
        return e;
    }
    return {
        type: 'unknown',
        title: 'Error',
        detail: `{e}`,
    };
}

const generationIdSelector = (d: Dataset) => d.generationID;
const datasetIdSelector = (d: Dataset) => d.uid;
const columnsByKeySelector = (d: Dataset) => d.columnsByKey;
const localDataSelector = (d: Dataset) => d.columnData;

function useCell(
    columnKey: string,
    row: number,
    fetchDelay = 0
): [unknown | null | undefined, Problem | undefined] {
    const datasetId = useDataset(datasetIdSelector) ?? '';
    const generationId = useDataset(generationIdSelector);
    const columnsByKey = useDataset(columnsByKeySelector);
    const localData = useDataset(localDataSelector);

    const dtype = columnsByKey[columnKey].type;
    const localValue = localData[columnKey][row];

    const [remoteValue, setRemoteValue] = useState<unknown | null>();
    const [problem, setProblem] = useState<Problem>();

    useEffect(() => {
        if (!dtype.lazy) return;
        _getCell(datasetId, columnKey, row, generationId, dtype.binary, fetchDelay)
            .then((v: unknown) => {
                setRemoteValue(v);
                setProblem(undefined);
            })
            .catch((e) => setProblem(_errorToProblem(e)));
    }, [datasetId, columnKey, row, generationId, dtype, fetchDelay]);

    return [dtype.lazy ? localValue : remoteValue, problem];
}

export function useRow(
    row: number,
    columnKeys: Array<string>,
    fetchDelay = 0
): [Record<string, unknown> | undefined, Problem | undefined] {
    const datasetId = useDataset(datasetIdSelector) ?? '';
    const generationId = useDataset(generationIdSelector);
    const columnsByKey = useDataset(columnsByKeySelector);
    const localData = useDataset(localDataSelector);

    const [values, setValues] = useState<Record<string, unknown>>();
    const [problem, setProblem] = useState<Problem>();

    useEffect(() => {
        const promises = columnKeys.map((key) => {
            const dtype = columnsByKey[key].type;
            if (dtype.lazy) {
                return _getCell(
                    datasetId,
                    key,
                    row,
                    generationId,
                    dtype.binary,
                    fetchDelay
                );
            } else {
                return Promise.resolve(localData[key][row]);
            }
        });
        Promise.all(promises)
            .then((v) => {
                const keyedValues: Record<string, unknown> = {};
                for (let i = 0; i < columnKeys.length; ++i) {
                    keyedValues[columnKeys[i]] = v[i];
                }
                setValues(keyedValues);
                setProblem(undefined);
            })
            .catch((e) => setProblem(_errorToProblem(e)));
    }, [datasetId, row, columnKeys, generationId, columnsByKey, localData, fetchDelay]);

    return [values, problem];
}

export default useCell;

import { useEffect, useState } from 'react';
import api from '../api';
import { Dataset, useDataset } from '../stores/dataset';
import { Problem, isProblem } from '../types';

interface CachedCell {
    generationId: number;
    promise: Promise<unknown>;
}
const cellCacheCapacity = 100;
const cellCache: Map<string, CachedCell> = new Map();

async function _fetchCell(
    column: string,
    row: number,
    generationId: number,
    asBuffer: boolean
) {
    const response = await api.table.getCellRaw({ column, row, generationId });
    if (asBuffer) {
        return response.raw.arrayBuffer();
    } else {
        return response.value();
    }
}

async function _sleep(ms: number) {
    await new Promise((resolve) => setTimeout(resolve, ms));
}

function _getCell(
    column: string,
    row: number,
    generationId: number,
    asBuffer: boolean,
    fetchDelay = 0
) {
    const cacheKey = `${column},${row},${asBuffer}`;
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

function useCell(
    columnKey: string,
    row: number,
    fetchDelay = 0
): [unknown | null | undefined, Problem | undefined] {
    const generationId = useDataset(generationIdSelector);
    const dtype = useDataset((d) => d.columnsByKey[columnKey].type);

    const localValue = useDataset((d) => d.columnData[columnKey][row]);

    const [remoteValue, setRemoteValue] = useState<unknown | null>();
    const [problem, setProblem] = useState<Problem>();

    useEffect(() => {
        if (!dtype.lazy) return;
        _getCell(columnKey, row, generationId, dtype.binary, fetchDelay)
            .then((v: unknown) => {
                setRemoteValue(v);
                setProblem(undefined);
            })
            .catch((e) => setProblem(_errorToProblem(e)));
    }, [columnKey, row, generationId, dtype, fetchDelay]);

    return [dtype.lazy ? localValue : remoteValue, problem];
}

export function useRow(
    row: number,
    columnKeys: Array<string>,
    fetchDelay = 0
): [Record<string, unknown> | undefined, Problem | undefined] {
    const generationId = useDataset(generationIdSelector);
    const columnsByKey = useDataset((d) => d.columnsByKey);
    const columnData = useDataset((d) => d.columnData);

    const [values, setValues] = useState<Record<string, unknown>>();
    const [problem, setProblem] = useState<Problem>();

    useEffect(() => {
        const promises = columnKeys.map((key) => {
            const dtype = columnsByKey[key].type;
            if (dtype.lazy) {
                return _getCell(key, row, generationId, dtype.binary, fetchDelay);
            } else {
                return Promise.resolve(columnData[key][row]);
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
    }, [row, columnKeys, generationId, columnsByKey, columnData, fetchDelay]);

    return [values, problem];
}

export default useCell;

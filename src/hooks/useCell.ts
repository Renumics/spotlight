import { useEffect, useState } from 'react';
import api from '../api';
import { Dataset, useDataset } from '../stores/dataset';

interface CachedCell {
    column: string;
    row: number;
    generationId: number;
    promise: Promise<unknown>;
}
const cellCache: Record<string, CachedCell> = {};

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

async function _getCell(
    column: string,
    row: number,
    generationId: number,
    asBuffer: boolean,
    fetchDelay = 0
) {
    const cacheKey = `${column},${row},${asBuffer}`;
    let cell = cellCache[cacheKey];
    if (cell?.generationId != generationId) {
        if (fetchDelay) _sleep(fetchDelay);
        const promise = _fetchCell(column, row, generationId, asBuffer);
        cell = {
            column,
            row,
            generationId,
            promise,
        };
        cellCache[cacheKey] = cell;
    }
    return cell.promise;
}

const generationIdSelector = (d: Dataset) => d.generationID;

function useCell(
    columnKey: string,
    row: number,
    fetchDelay = 0
): unknown | null | undefined {
    const generationId = useDataset(generationIdSelector);
    const dtype = useDataset((d) => d.columnsByKey[columnKey].type);

    const localValue = useDataset((d) => d.columnData[columnKey][row]);

    const [remoteValue, setRemoteValue] = useState<unknown | null>();
    useEffect(() => {
        if (!dtype.lazy) return;
        _getCell(columnKey, row, generationId, dtype.binary, fetchDelay).then(
            (v: any) => {
                setRemoteValue(v);
            }
        );
    }, [columnKey, row, generationId, dtype, fetchDelay]);

    return dtype.lazy ? localValue : remoteValue;
}

export function useRow(
    row: number,
    columnKeys: Array<string>,
    fetchDelay = 0
): Record<string, unknown> | undefined {
    const generationId = useDataset(generationIdSelector);
    const columnsByKey = useDataset((d) => d.columnsByKey);
    const columnData = useDataset((d) => d.columnData);

    const [values, setValues] = useState<Record<string, unknown>>();

    useEffect(() => {
        const promises = columnKeys.map((key) => {
            const dtype = columnsByKey[key].type;
            if (dtype.lazy) {
                return _getCell(key, row, generationId, dtype.binary, fetchDelay);
            } else {
                return Promise.resolve(columnData[key][row]);
            }
        });
        Promise.all(promises).then((v) => {
            const keyedValues: Record<string, unknown> = {};
            for (let i = 0; i < columnKeys.length; ++i) {
                keyedValues[columnKeys[i]] = v[i];
            }
            setValues(keyedValues);
        });
    }, [row, columnKeys, generationId, columnsByKey, columnData, fetchDelay]);

    return values;
}

export default useCell;

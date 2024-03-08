import type { DataColumn } from './dataset';
import type { DataType } from '../datatypes';

export type LensKey = string;

export type LensSettings = Record<string, unknown>;

export interface LensProps<T = unknown> {
    value: T;
    values: T[];
    column: DataColumn;
    columns: DataColumn[];
    rowIndex: number;
    url?: string;
    urls: (string | undefined)[];
    syncKey?: string;
}

interface LensAttributes {
    displayName: string;
    key: LensKey;
    dataTypes: DataType['kind'][];
    multi?: boolean;
    isEditor?: boolean;
    minHeight?: number;
    maxHeight?: number;
    defaultHeight?: number;
    filterAllowedColumns?: (
        allColumns: DataColumn[],
        selectedColumns: DataColumn[]
    ) => DataColumn[];
    isSatisfied?: (columns: DataColumn[]) => boolean;
    handlesNull?: boolean;
}

export type Lens<T = unknown> = React.FunctionComponent<LensProps<T>> & LensAttributes;

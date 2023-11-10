import type { DataColumn } from './dataset';
import type { DataType } from '../datatypes';

export type LensKind = string;

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
    kind: LensKind;
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
}

export type Lens<T = unknown> = React.FunctionComponent<LensProps<T>> & LensAttributes;

export interface LensSpec {
    kind: LensKind;
    key: string;
    name: string;
    columns: string[];
}

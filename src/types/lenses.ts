import type { DataColumn } from './dataset';
import type { DataType } from '../datatypes';
import { Settings } from '../systems/lenses/types';

export type LensKind = string;

export interface LensProps<T, S extends Settings = Settings> {
    value: T;
    values: T[];
    column: DataColumn;
    columns: DataColumn[];
    rowIndex: number;
    url?: string;
    urls: (string | undefined)[];
    groupKey: string;
    settings: S;
}

interface LensAttributes<S extends Settings = Settings> {
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
    settings?: S;
}

export type Lens<T = unknown, S extends Settings = Settings> = React.FunctionComponent<
    LensProps<T, S>
> &
    LensAttributes<S>;

export interface LensSpec<S extends Settings = Settings> {
    kind: LensKind;
    key: string;
    name: string;
    columns: string[];
    settings?: S;
}

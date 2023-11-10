import type { DataColumn } from './dataset';
import type { DataType } from '../datatypes';

export type LensKind = string;

export interface LensProps<T = unknown, S = unknown> {
    value: T;
    values: T[];
    column: DataColumn;
    columns: DataColumn[];
    rowIndex: number;
    url?: string;
    urls: (string | undefined)[];
    syncKey?: string;
    settings?: S;
}

interface MenuProps<S> {
    settings?: S;
}

interface LensAttributes<S> {
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
    menu?: (props: MenuProps<S>) => JSX.Element;
}

export type Lens<T = unknown, S = unknown> = React.FunctionComponent<LensProps<T, S>> &
    LensAttributes<S>;

export interface LensSpec<S = unknown> {
    kind: LensKind;
    key: string;
    name: string;
    columns: string[];
    settings?: S;
}

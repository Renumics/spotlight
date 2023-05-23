import { DataType } from '../datatypes';
import { DataColumn } from '../types';

export interface ViewProps<T = unknown> {
    value: T;
    values: T[];
    column: DataColumn;
    columns: DataColumn[];
    rowIndex: number;
    url?: string;
    urls: (string | undefined)[];
    syncKey?: string;
}

interface ViewAttributes {
    displayName: string;
    key?: string;
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
export type View<T = unknown> = React.FunctionComponent<ViewProps<T>> & ViewAttributes;

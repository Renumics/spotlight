import { DataKind } from '../../datatypes';

export type ValueArray = number[] | Int32Array | boolean[] | string;

export interface Metric {
    signature: Record<string, DataKind | DataKind[]>;
    compute: (values: ValueArray[]) => number;
}

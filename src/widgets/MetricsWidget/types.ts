import { DataKind } from '../../datatypes';

export type ValueArray = number[] | Int32Array | boolean[];

export interface Metric {
    signature: Record<string, DataKind | DataKind[]>;
    compute: (values: ValueArray[]) => number;
}

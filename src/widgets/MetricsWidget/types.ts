export type ValueArray = number[] | Int32Array;

export interface Metric {
    compute: (values: ValueArray) => number;
}

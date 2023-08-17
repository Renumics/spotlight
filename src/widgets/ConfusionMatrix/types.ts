export interface Bucket {
    rows: number[];
}

export interface MatrixData {
    xNames: string[];
    yNames: string[];
    buckets: Bucket[];
}

export interface Cell {
    x: number;
    y: number;
    bucket: Bucket;
}

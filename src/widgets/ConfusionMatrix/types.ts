type Value = string | number;

interface Bucket {
    x: number;
    y: number;
    rows: number[];
}

interface MatrixData {
    xNames: string[];
    yNames: string[];
    buckets: Bucket[];
}

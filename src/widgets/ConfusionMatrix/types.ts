type Value = string | number;

interface Bucket {
    rows: number[];
}

interface MatrixData {
    xNames: string[];
    yNames: string[];
    buckets: Bucket[];
}

interface Cell {
    x: number;
    y: number;
    bucket: Bucket;
}

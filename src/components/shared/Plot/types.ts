export interface Margin {
    left: number;
    right: number;
    top: number;
    bottom: number;
}

export type Point2d = [number, number];

export type MergeStrategy = 'replace' | 'union' | 'difference' | 'intersect';

import * as d3 from 'd3';

export type HistogramType = 'discrete' | 'continuous';

export interface HistogramData {
    xBins: Bin[];
    yBins: Bin[];
    all: Stack[];
    filtered: Stack[];
    kind: HistogramType;
    binToRowIndices: Map<BinKey, Map<BinKey, number[]>>;
    xColumnName?: string;
    yColumnName?: string;
}

export type Bucket = d3.SeriesPoint<{ [key: string]: number }> & {
    yKey: BinKey;
    yBin: number;
    xKey: BinKey;
    xBin: number;
};

export type Stack = Bucket[];

export type BinKey = number | string | boolean;

export type Bin = {
    index: number;
    key: BinKey;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value: any;
    min: number;
    max: number;
};

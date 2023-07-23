import * as d3 from 'd3';
import { useCallback, useMemo } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import { ColumnData, DataColumn, isCategoricalColumn } from '../../types';
import { Bin, BinKey, HistogramData, HistogramType } from './types';

const MAX_BUCKETS_X = 50;
const MAX_BUCKETS_Y = 50;

/**
 * order a series of continuous datapoints into bins
 * returns the generated bins and a list with an entry for each datapoint in columnData specifiing the bin
 * this row was assigned to or undefined if it was not assigned at all
 *
 * Bin.min and Bin.max are set to the minimal/maximal value of the bin
 * @param {ColumnData} columnData values of the column that should be binned
 * @returns {Bin[], number[]}
 */
function binContinuousData(
    columnData: ColumnData,
    maxBuckets: number
): [Bin[], (number | undefined)[]] {
    const data = Array(columnData.length)
        .fill(0)
        .map((_, i) => [columnData[i], i]);
    const values = data.map(([value]) => value);

    const scale = d3
        .scaleLinear()
        .domain(d3.extent(values) as [number, number])
        .nice();

    const domain = scale.domain() as [number, number];

    const thresholds = Math.min(
        maxBuckets,
        d3.thresholdScott(values, domain[0], domain[1])
    );

    const bin = d3
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .bin<any, number>()
        .domain(domain)
        .thresholds(thresholds)
        .value((x) => x[0]);

    const bins = bin(data);

    scale.range([0, bins.length]);

    const binnedIds = new Map(
        bins
            .map((b, binIndex) =>
                b.map(([, index]): [number, number] => [index, binIndex])
            )
            .flat()
    );

    return [
        bins.map((b, index) => {
            const min = b.x0 as number;
            const max = b.x1 as number;

            return {
                index,
                key: `${b.x0}-${b.x1}`,
                value: (min + max) / 2,
                min,
                max,
            };
        }),
        Array(columnData.length)
            .fill(0)
            .map((_, i) => binnedIds.get(i)),
    ];
}

/**
 * order a series of discrete datapoints into bins
 * returns the generated bins and a list with an entry for each datapoint in columnData specifiing the bin
 * this row was assigned to or undefined if it was not assigned at all
 *
 * Bin.min and Bin.max are set to the index of the current bin and this index + 1
 * @param {ColumnData} columnData values of the column that should be binned
 * @returns {Bin[], number[]}
 */
function binDiscreteData(
    columnData: ColumnData,
    column?: DataColumn
): [Bin[], (BinKey | undefined)[]] {
    const data = Array(columnData.length)
        .fill(0)
        .map((_, i) => [columnData[i], i]);

    const unorderedCounts = d3.rollup(
        data,
        (group) => group.map(([, i]) => i),
        ([value]) => value
    );

    const categorical = column && isCategoricalColumn(column);

    const orderedKeys = [...unorderedCounts.keys()].sort((a, b) =>
        categorical
            ? column.type.invertedCategories[a] > column.type.invertedCategories[b]
                ? 1
                : -1
            : a - b
    );

    const binnedIds = new Map(
        orderedKeys
            .map((key, binIndex) =>
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                unorderedCounts.get(key)!.map((id): [number, number] => [id, binIndex])
            )
            .flat()
    );

    const bins = orderedKeys.map((key, index) => ({
        index,
        key: categorical ? column.type.invertedCategories[key] : key,
        value: key,
        min: index,
        max: index + 1,
    }));

    return [
        bins,
        Array(columnData.length)
            .fill(0)
            .map((_, i) => binnedIds.get(i)),
    ];
}

const isRowFilteredSelector = (d: Dataset) => d.isIndexFiltered;

function useHistogram(xColumnKey?: string, yColumnKey?: string): HistogramData {
    const isRowFiltered = useDataset(isRowFilteredSelector);

    const columnsSelector = useCallback(
        (d: Dataset): [DataColumn | undefined, DataColumn | undefined] => [
            d.columns.find((col) => col?.key === xColumnKey),
            yColumnKey !== undefined
                ? d.columns.find((col) => col?.key === yColumnKey)
                : undefined,
        ],
        [xColumnKey, yColumnKey]
    );
    const [xColumn, yColumn] = useDataset(columnsSelector);

    const xColumnDataSelector = useCallback(
        (d: Dataset) => d.columnData[xColumnKey ?? -1],
        [xColumnKey]
    );
    const yColumnDataSelector = useCallback(
        (d: Dataset) => d.columnData[yColumnKey ?? -1],
        [yColumnKey]
    );
    const xColumnData = useDataset(xColumnDataSelector);
    const yColumnData = useDataset(yColumnDataSelector);

    const binData = useCallback(
        /**
         * bin the data of a column based on its type and the resulting number of bins
         * @param {ColumnData} data the data of the column to be binned
         * @param {DataColumn} column the column to be binned
         * @returns {Bin[], number[]}
         */
        (
            data: ColumnData,
            column: DataColumn,
            maxBuckets: number
        ): [Bin[], (BinKey | undefined)[], HistogramType] => {
            if (!column) return [[] as Bin[], [], 'discrete'];

            if (column.type.kind === 'float') {
                const [bins, binned] = binContinuousData(data, maxBuckets);
                return [bins, binned, 'continuous'];
            }
            if (column.type.kind === 'int') {
                const [bins, d] = binDiscreteData(data, column);

                if (bins.length > maxBuckets) {
                    const [bins, binned] = binContinuousData(data, maxBuckets);
                    return [bins, binned, 'continuous'];
                }
                return [bins, d, 'discrete'];
            }

            const [bins, binned] = binDiscreteData(data, column);

            return [bins, binned, 'discrete'];
        },
        []
    );

    const [xBins, xBinnedData, histogramType] = useMemo(() => {
        if (xColumn === undefined) return [[], [], 'discrete' as HistogramType];
        return binData(xColumnData, xColumn, MAX_BUCKETS_X);
    }, [binData, xColumn, xColumnData]);

    const [yBins, yBinnedData] = useMemo(() => {
        if (yColumn === undefined) return [[], []];
        return binData(yColumnData, yColumn, MAX_BUCKETS_Y);
    }, [binData, yColumn, yColumnData]);

    const [allStack, filteredStack, binKeyToIndices] = useMemo(
        /**
         * generate stacked data for all and filtered data points based on two binned columns and
         * a 2 dimensional map mapping x and y Bins keys to all included row indices
         *
         */
        () => {
            const binnedData = xBinnedData.map((xBin, index) => ({
                index,
                xBin,
                yBin: yBinnedData[index],
            }));

            const xBinIndexMap = new Map(xBins.map(({ key, index }) => [index, key]));
            const yBinIndexMap = new Map(yBins.map(({ key, index }) => [index, key]));

            // combine both binned columns together into one {rowIndex, xBinIndex, yBinIndex}[]
            const valid = binnedData
                .filter(
                    ({ xBin, yBin }) =>
                        xBin !== undefined &&
                        (yColumn === undefined || yBin !== undefined)
                )
                .map((v) => ({ ...v, yBin: v.yBin ?? 0 })) as {
                index: number;
                xBin: number;
                yBin: number;
            }[];

            /**
             * stack data in order to use the d3 dataformat for stacked bar charts
             * see an example at https://observablehq.com/@d3/stacked-bar-chart
             *
             * the resulting stack basically has this shape:
             *
             * [
             *  [x0y0, x1y0, x2y0],
             *  [x0y1, x1y1, x2y1],
             *  [x0y2, x1y2, x2y1]
             * ]
             *
             * where e.g. x0y1  stores the vertical start and end of the second bucket in the first stack
             *                  additionaly the bins indices and keys are stored in x0y1 resulting in
             *                  x0y1.data stores all counts of bins in this stack so: x0y0 x0y1 x0y2
             *
             *                  [0:x0y1Start 1:x0y1End data: {y0Key: 14, y1Key: 3, y2Key: 3, xBin: x0Key} xBin: x0Index(0) xKey:x0Key yBin:y0Index(1) yKey:y1Key]
             *
             *
             * @param data
             * @returns {[Map<BinKey, Map<BinKey, number>>, Stack[]]}
             */
            const stackData = (
                data: typeof valid
            ): [
                Map<BinKey, Map<BinKey, number[]>>,
                (d3.SeriesPoint<{
                    [key: string]: number;
                }> & {
                    yKey: BinKey;
                    yBin: number;
                    xKey: BinKey;
                    xBin: number;
                })[][]
            ] => {
                // generate a map [xBinIndex][yBinIndex] => [...rowIdxInBin]
                const binToRowIndexMap = d3.rollup(
                    data,
                    (g) => g.map(({ index }) => index),
                    (d) => d.xBin,
                    (d) => (yBins.length > 0 ? d.yBin : 0)
                );

                const mapped = [...binToRowIndexMap.entries()].map(([xBin, group]) => {
                    if (yBins.length > 0) {
                        return {
                            xBin,
                            ...Object.fromEntries(
                                [...group.entries()].map(([i, g]) => [i, g.length])
                            ),
                        };
                    } else {
                        return {
                            xBin,
                            ...{
                                0: [...group.values()].reduce(
                                    (p, g) => p + g.length,
                                    0
                                ),
                            },
                        };
                    }
                });

                const stacked = d3
                    .stack<
                        {
                            [key: string]: number;
                        },
                        number
                    >()
                    .keys(yBins.length > 0 ? yBins.map(({ index }) => index) : [0])(
                        mapped
                    )
                    .map((s) => {
                        return s.map((d) => {
                            return Object.assign(d, {
                                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                                yKey: yBinIndexMap.get(s.key)!,
                                yBin: s.index,
                                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                                xKey: xBinIndexMap.get(d.data.xBin)!,
                                xBin: d.data.xBin,
                            });
                        });
                    });
                return [binToRowIndexMap, stacked];
            };

            const [binKeyToIndices, allStack] = stackData(valid);

            const filtered = valid.filter(({ index }) => isRowFiltered[index]);

            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const [_, filteredStack] = stackData(filtered);

            return [allStack, filteredStack, binKeyToIndices];
        },
        [isRowFiltered, xBinnedData, xBins, yBinnedData, yBins, yColumn]
    );

    return {
        xBins,
        yBins,
        all: allStack,
        filtered: filteredStack,
        kind: histogramType,
        binToRowIndices: binKeyToIndices,
        xColumnName: xColumnKey,
        yColumnName: yColumnKey,
    };
}

export default useHistogram;

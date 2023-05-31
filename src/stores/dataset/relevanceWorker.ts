import * as Comlink from 'comlink';
import * as d3 from 'd3';
import {
    DataColumn,
    isCategoricalColumn,
    isNumberColumn,
    TableData,
} from '../../types';
import distances from '../../math/distances';

const worker = {
    computeRelevances(
        columns: DataColumn[],
        data: TableData,
        foregroundIndices: number[],
        backgroundIndices: number[]
    ) {
        let maxRelevance = 0;
        const relevanceMap = new Map<string, number>();

        const backgroundValues = new Array(backgroundIndices.length);
        const foregroundValues = new Array(foregroundIndices.length);

        columns.forEach((column: DataColumn) => {
            if (!(isNumberColumn(column) || isCategoricalColumn(column))) return;

            let min = Infinity;
            let max = -Infinity;

            for (let i = 0; i < backgroundValues.length; i++) {
                const value = data[column.key][backgroundIndices[i]];
                backgroundValues[i] = value;
                if (value < min) min = value;
                if (value > max) max = value;
            }

            for (let i = 0; i < foregroundValues.length; i++) {
                const value = data[column.key][foregroundIndices[i]];
                foregroundValues[i] = value;
                if (value < min) min = value;
                if (value > max) max = value;
            }

            if (backgroundValues.length === 0 || foregroundValues.length === 0) return;

            // min/max can return undefined if all the numbers are NaN
            // in this case we stop the computation
            // and return a relevance value of zero
            if (min === undefined || max === undefined) {
                return;
            }

            const makeHistogram = d3.bin().domain([min, max]).thresholds(5);

            const filteredDistribution = makeHistogram(backgroundValues).map(
                (b) => b.length / backgroundValues.length
            );
            const selectedDistribution = makeHistogram(foregroundValues).map(
                (b) => b.length / foregroundValues.length
            );

            const relevance = distances.bhattacharyya(
                selectedDistribution,
                filteredDistribution
            );

            if (relevance > maxRelevance) {
                maxRelevance = relevance;
            }

            relevanceMap.set(column.key, relevance);
        });

        if (maxRelevance === 0) {
            return relevanceMap;
        }

        // normalize relevance values
        relevanceMap.forEach((relevance, key, map) => {
            map.set(key, relevance / maxRelevance);
        });

        return relevanceMap;
    },
};

Comlink.expose(worker);

import { IndexArray } from '../types';
import taskService from './task';

export const umapMetricNames = [
    'euclidean',
    'standardized euclidean',
    'robust euclidean',
    'cosine',
    'mahalanobis',
] as const;
export type UmapMetric = (typeof umapMetricNames)[number];
export const pcaNormalizations = ['none', 'standardize', 'robust standardize'] as const;
export type PCANormalization = (typeof pcaNormalizations)[number];

interface ReductionResult {
    points: [number, number][];
    indices: IndexArray;
}

export class DataService {
    async computeUmap(
        widgetId: string,
        columnNames: string[],
        indices: IndexArray,
        n_neighbors: number,
        metric: UmapMetric,
        min_dist: number
    ): Promise<ReductionResult> {
        return await taskService.run('umap', widgetId, {
            column_names: columnNames,
            indices: Array.from(indices),
            n_neighbors,
            metric,
            min_dist,
        });
    }

    async computePCA(
        widgetId: string,
        columnNames: string[],
        indices: IndexArray,
        pcaNormalization: PCANormalization
    ): Promise<ReductionResult> {
        return await taskService.run('pca', widgetId, {
            indices: Array.from(indices),
            column_names: columnNames,
            normalization: pcaNormalization,
        });
    }
}

const dataService = new DataService();
export default dataService;

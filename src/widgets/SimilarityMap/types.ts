export const reductionMethods = ['umap', 'pca'] as const;

export type ReductionMethod = (typeof reductionMethods)[number];

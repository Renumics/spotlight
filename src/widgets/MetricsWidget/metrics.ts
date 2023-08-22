import _ from 'lodash';
import { Metric } from './types';

export const METRICS: Record<string, Metric> = {
    sum: {
        compute: _.sum,
    },
    mean: {
        compute: _.mean,
    },
    min: {
        compute: (values) => _.min(values) ?? NaN,
    },
    max: {
        compute: (values) => _.max(values) ?? NaN,
    },
    count: {
        compute: (values) => values.length,
    },
};

import _ from 'lodash';
import { Metric } from './types';

export const METRICS: Record<string, Metric> = {
    sum: {
        signature: {
            X: ['int', 'float'],
        },
        compute: ([values]) => _(values).reject(_.isNaN).sum(),
    },
    mean: {
        signature: {
            X: ['int', 'float'],
        },
        compute: ([values]) => _(values).reject(_.isNaN).mean(),
    },
    min: {
        signature: {
            X: ['int', 'float'],
        },
        compute: ([values]) => _.min(values as number[]) ?? NaN,
    },
    max: {
        signature: {
            X: ['int', 'float'],
        },
        compute: ([values]) => _.max(values as number[]) ?? NaN,
    },
    count: {
        signature: {
            X: ['int', 'float'],
        },
        compute: ([values]) => values.length,
    },
    'F-Score': {
        signature: {
            X: ['bool'],
            Y: ['bool'],
        },
        compute: ([actualValues, assignedValues]) => {
            let tp = 0;
            let fp = 0;
            let fn = 0;

            for (let i = 0; i < actualValues.length; i++) {
                const actualValue = actualValues[i];
                const assignedValue = assignedValues[i];
                if (assignedValue) {
                    if (actualValue) {
                        tp++;
                    } else {
                        fp++;
                    }
                } else if (actualValue) {
                    fn++;
                }
            }
            return (2 * tp) / (2 * tp + 2 * fp + fn);
        },
    },
    MCC: {
        signature: {
            X: ['bool'],
            Y: ['bool'],
        },
        compute: ([actualValues, assignedValues]) => {
            let tp = 0;
            let fp = 0;
            let tn = 0;
            let fn = 0;

            for (let i = 0; i < actualValues.length; i++) {
                const actualValue = actualValues[i];
                const assignedValue = assignedValues[i];
                if (assignedValue) {
                    if (actualValue) {
                        tp++;
                    } else {
                        fp++;
                    }
                } else if (actualValue) {
                    fn++;
                } else {
                    tn++;
                }
            }

            if (tp + tn === actualValues.length) return 1;
            if (fp + fn === actualValues.length) return 0;

            return (
                (tp * tn - fp * fn) /
                Math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
            );
        },
    },
};

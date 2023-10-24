import _ from 'lodash';
import { Metric } from './types';
import { computeConfusion } from './confusion';

export const METRICS: Record<string, Metric> = {
    sum: {
        signature: {
            X: ['int', 'float', 'bool'],
        },
        compute: ([values]) => +_(values).reject(_.isNaN).sum() ?? NaN,
    },
    mean: {
        signature: {
            X: ['int', 'float', 'bool'],
        },
        compute: ([values]) => +_(values).reject(_.isNaN).mean() ?? NaN,
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
    accuracy: {
        signature: {
            X: ['bool', 'int', 'Category'],
            Y: ['bool', 'int', 'Category'],
        },
        compute: ([actualValues, assignedValues]) => {
            const all = actualValues.length;
            let correct = 0;

            for (let i = 0; i < actualValues.length; i++) {
                const actual = actualValues[i];
                const assigned = assignedValues[i];

                if (actual === assigned) {
                    correct++;
                }
            }

            return correct / all;
        },
    },
    F1: {
        signature: {
            X: ['bool'],
            Y: ['bool'],
        },
        compute: ([actualValues, assignedValues]) => {
            const {
                truePositives: tp,
                falsePositives: fp,
                falseNegatives: fn,
            } = computeConfusion(
                actualValues as boolean[],
                assignedValues as boolean[]
            );

            return (2 * tp) / (2 * tp + fp + fn);
        },
    },
    MCC: {
        signature: {
            X: ['bool'],
            Y: ['bool'],
        },
        compute: ([actualValues, assignedValues]) => {
            const {
                truePositives: tp,
                trueNegatives: tn,
                falsePositives: fp,
                falseNegatives: fn,
            } = computeConfusion(
                actualValues as boolean[],
                assignedValues as boolean[]
            );

            if (tp + tn === actualValues.length) return 1;
            if (fp + fn === actualValues.length) return 0;

            return (
                (tp * tn - fp * fn) /
                Math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
            );
        },
    },
};

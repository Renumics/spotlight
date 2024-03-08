import _ from 'lodash';

export interface Problem {
    type: string;
    title: string;
    detail?: string;
    instance?: string;
}

export function isProblem(error: unknown): error is Problem {
    return _.isObject(error) && 'type' in error && 'title' in error;
}

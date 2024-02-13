import { Problem } from '../types';

const DEFAULT_PROBLEM: Problem = {
    type: 'UndefinedApiError',
    title: 'Undefined API Error',
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function parseError(error: any): Promise<Problem> {
    if (!error.response?.json) {
        return DEFAULT_PROBLEM;
    }

    try {
        return (await error.response.json()) as Problem;
    } catch {
        return DEFAULT_PROBLEM;
    }
}

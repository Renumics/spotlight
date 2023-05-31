import { ReactElement } from 'react';
import { toast, TypeOptions } from 'react-toastify';
import 'twin.macro';
import { Problem } from './types';

export const notify = (
    message: string | ReactElement = '',
    type: TypeOptions = 'info'
): void => {
    toast(message, {
        type,
    });
};

export const notifyError = (message: string | ReactElement): void => {
    notify(message, 'error');
};

export const notifyProblem = (problem: Problem, type: TypeOptions = 'error'): void => {
    if (problem.detail !== undefined) {
        notify(
            <div tw="flex-col flex">
                <span tw="font-semibold">{problem.title}</span>
                <span>{problem.detail}</span>
            </div>,
            type
        );
    } else {
        notify(problem.title, type);
    }
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types
export function notifyAPIError(error: any): void {
    if (!error.response?.json) {
        notifyError('Failed to reach backend');
        return;
    }

    error.response
        .json()
        .then((problem: Problem) => notifyProblem(problem))
        .catch(() => {
            notifyError('Failed to reach backend');
        });
}

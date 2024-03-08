import application from '../application';
import { useDataset } from '../lib';
import { Problem } from '../types';
import Center from './ui/Center';
import tw from 'twin.macro';

interface Props {
    problem: Problem;
}

const Button = tw.button`border border-gray-600 rounded px-2 py-1 text-sm`;

const LoadingError = ({ problem }: Props): JSX.Element => {
    const reload = () => location.reload();
    const browse = () => useDataset.getState().clearLoadingError();
    const close = () => window.close();

    return (
        <Center tw="flex flex-col gap-y-4 text-midnight-600">
            <div tw="flex flex-col items-center">
                <h1 tw="text-lg">Failed to load your dataset</h1>
                <p tw="text-sm text-gray-800">(with the following API error)</p>
            </div>
            <div tw="border border-red-600 rounded bg-red-100 divide-y divide-red-600">
                <h2 tw="font-bold p-1">{problem.title}</h2>
                {problem.detail && <p tw="p-1 text-sm">{problem.detail}</p>}
            </div>
            <div tw="flex flex-row gap-x-2">
                <Button onClick={reload}>Reload</Button>
                {application.filebrowsingAllowed && (
                    <Button onClick={browse}>Open another dataset</Button>
                )}
                <Button onClick={close}>Close</Button>
            </div>
        </Center>
    );
};

export default LoadingError;

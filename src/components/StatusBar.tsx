import application from '../application';
import CloseIcon from '../icons/X';
import { useCallback } from 'react';
import { Dataset, useDataset } from '../stores/dataset';
import { useMessages } from '../stores/messages';
import 'twin.macro';
import Button from './ui/Button';

const columnCountSelector = (d: Dataset) => d.columns.length;
const rowCountSelector = (d: Dataset) => d.length;

const StatusBar = (): JSX.Element => {
    const columnCount = useDataset(columnCountSelector);
    const rowCount = useDataset(rowCountSelector);
    const messages = useMessages();

    const error = messages.persistentErrors[0];
    const warning = messages.persistentWarnings[0];

    const closeError = useCallback(() => {
        messages.removePersistentError(error);
    }, [messages, error]);

    const closeWarning = useCallback(() => {
        messages.removePersistentWarning(warning);
    }, [messages, warning]);

    if (messages.persistentErrors.length) {
        return (
            <div tw="flex flex-row h-4 border-t border-red-600 bg-red-500 text-white font-bold text-xs items-center">
                <div tw="font-bold pl-1 pr-2">ERROR</div>
                <div tw="flex-grow">{messages.persistentErrors[0]}</div>
                <Button onClick={closeError}>
                    <CloseIcon />
                </Button>
            </div>
        );
    }

    if (messages.persistentWarnings.length) {
        return (
            <div tw="flex flex-row h-4 border-t border-orange-600 bg-orange-500 text-midnight-600 text-xs items-center">
                <div tw="font-bold pl-1 pr-2">WARNING</div>
                <div tw="flex-grow">{messages.persistentWarnings[0]}</div>
                <Button onClick={closeWarning}>
                    <CloseIcon />
                </Button>
            </div>
        );
    }

    return (
        <div tw="flex flex-row h-4 border-t border-gray-400 text-gray-800 text-xs items-center divide-x divide-gray-400 whitespace-nowrap">
            <div tw="pl-1 pr-2">
                {columnCount} cols / {rowCount} rows
            </div>
            <div tw="px-2">Spotlight {application.edition.name} Edition</div>
            <div tw="px-2">Version {application.version}</div>
            <div tw="flex-grow"></div>
            <div tw="px-1">
                <a
                    tw="hover:text-blue-600"
                    href="https://www.renumics.com"
                    target="_blank"
                    rel="noreferrer"
                >
                    built with ♥ by renumics
                </a>
            </div>
        </div>
    );
};

export default StatusBar;

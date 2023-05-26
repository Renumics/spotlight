import * as React from 'react';
import { useCallback, useEffect, useMemo } from 'react';
import type { FallbackProps } from 'react-error-boundary';
import { ErrorBoundary } from 'react-error-boundary';
import tw from 'twin.macro';
import LoadingIndicator from '../components/LoadingIndicator';
import useMemoWithPrevious from '../hooks/useMemoWithPrevious';
import { DataColumn } from '../types';
import { notifyAPIError } from '../notify';
import LensContext from './LensContext';
import registry, { LensKey, isLensCompatible } from './registry';
import useCellValues from './useCellValue';
import None from './None';

interface Props {
    view: LensKey;
    columns: DataColumn[];
    rowIndex: number;
    syncKey: string;
}

const Info = tw.div`w-full h-full flex items-center justify-center text-gray-800 italic text-sm p-2 text-center`;

const ErrorFallback = ({
    error,
    message,
}: {
    error: FallbackProps['error'];
    message?: string;
}) => {
    return (
        <div tw="w-full h-full flex justify-center items-center">
            <div tw="text-center font-bold uppercase text-sm text-gray-700">
                {message ? <p>{message}</p> : <p>Error Creating View.</p>}
                <p>{`${error.message}`}</p>
            </div>
        </div>
    );
};

const ViewFactory: React.FunctionComponent<Props> = ({
    view,
    columns,
    rowIndex,
    syncKey,
}) => {
    const columnKeys = useMemo(() => columns.map((c) => c.key), [columns]);
    const [values, problem] = useCellValues(rowIndex, columnKeys);

    const ViewComponent = registry.views[view];

    const urls = useMemoWithPrevious(
        (previousUrls: (string | undefined)[] | undefined) => {
            if (!values) return;
            if (previousUrls) return previousUrls;

            return values.map((value) => {
                if (value instanceof ArrayBuffer) {
                    const bufferView = new Uint8Array(value as ArrayBuffer);
                    const blob = new Blob([bufferView]);
                    return URL.createObjectURL(blob);
                } else {
                    return undefined;
                }
            });
        },
        [values],
        undefined
    );

    useEffect(() => {
        return () =>
            urls?.forEach((url) => {
                if (url) URL.revokeObjectURL(url);
            });
    }, [urls]);

    const types = columns.map((c) => c.type);
    const allEditable = columns.every((c) => c.editable);

    const fallbackRenderer = useCallback(
        ({ error }: FallbackProps) => (
            <ErrorFallback
                error={error}
                message={`Error Creating ${ViewComponent.displayName}.`}
            />
        ),
        [ViewComponent]
    );

    if (problem) return <Info>Failed to load value!</Info>;
    if (!values || !urls) return <LoadingIndicator delay={100} />;
    if (!ViewComponent) return <Info>View not found ({view})!</Info>;
    if (!isLensCompatible(ViewComponent, types, allEditable))
        return <Info>Incompatible View ({view})</Info>;

    const context = { syncKey };

    return (
        <LensContext.Provider value={context}>
            <ErrorBoundary fallbackRender={fallbackRenderer}>
                {values[0] == null ? (
                    <None />
                ) : (
                    <ViewComponent
                        url={urls[0]}
                        urls={urls}
                        value={values[0]}
                        values={values}
                        column={columns[0]}
                        columns={columns}
                        rowIndex={rowIndex}
                        syncKey={syncKey}
                    />
                )}
            </ErrorBoundary>
        </LensContext.Provider>
    );
};

export default ViewFactory;

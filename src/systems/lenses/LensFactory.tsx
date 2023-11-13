import * as React from 'react';
import _ from 'lodash';
import { useCallback, useEffect, useMemo } from 'react';
import type { FallbackProps } from 'react-error-boundary';
import { ErrorBoundary } from 'react-error-boundary';
import tw from 'twin.macro';
import LoadingIndicator from '../../components/LoadingIndicator';
import useMemoWithPrevious from '../../hooks/useMemoWithPrevious';
import { DataColumn, LensSpec } from '../../types';
import LensContext from './LensContext';
import useCellValues from './useCellValue';
import None from '../../lenses/None';
import { isLensCompatible, useComponentsStore } from '../../stores/components';
import { Dataset, useDataset } from '../../lib';

interface Props {
    spec: LensSpec;
    columns: DataColumn[];
    rowIndex: number;
    deferLoading?: boolean;
    onChange?: (spec: LensSpec) => void;
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

const columnsSelector = (d: Dataset) => d.columnsByKey;

const LensFactory: React.FunctionComponent<Props> = ({
    spec,
    rowIndex,
    deferLoading = false,
}) => {
    const allColumns = useDataset(columnsSelector);
    const columns = useMemo(
        () => spec.columns.map((colKey: string) => allColumns[colKey]),
        [allColumns, spec.columns]
    );

    const [values, problem] = useCellValues(rowIndex, spec.columns, deferLoading);

    const lenses = useComponentsStore((state) => state.lensesByKey);
    const LensComponent = lenses[spec.kind];

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

    const fallbackRenderer = useCallback(
        ({ error }: FallbackProps) => (
            <ErrorFallback
                error={error}
                message={`Error Creating ${LensComponent.displayName}.`}
            />
        ),
        [LensComponent]
    );

    const types = columns.map((c) => c.type);
    const allEditable = columns.every((c) => c.editable);

    if (problem) return <Info>Failed to load value!</Info>;
    if (!values || !urls) return <LoadingIndicator delay={100} />;
    if (!LensComponent) return <Info>Lens not found ({spec.kind})!</Info>;
    if (!isLensCompatible(LensComponent, types, allEditable))
        return <Info>Incompatible Lens ({spec.kind})</Info>;

    const context = { groupKey: spec.key, settings: {}, changeSettings: () => null };

    const allValuesAreNull = values.every(_.isNull);

    return (
        <LensContext.Provider value={context}>
            <ErrorBoundary fallbackRender={fallbackRenderer}>
                {allValuesAreNull ? (
                    <None />
                ) : (
                    <LensComponent
                        url={urls[0]}
                        urls={urls}
                        value={values[0]}
                        values={values}
                        column={columns[0]}
                        columns={columns}
                        rowIndex={rowIndex}
                        syncKey={spec.key}
                        settings={spec.settings ?? { foo: 5 }}
                    />
                )}
            </ErrorBoundary>
        </LensContext.Provider>
    );
};

export default LensFactory;

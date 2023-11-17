import LineChart, { Handle as LineChartRef } from '../../components/LineChart';
import _ from 'lodash';
import { useCallback, useMemo, useRef, useState } from 'react';
import { useColors } from '../../stores/colors';
import tw, { styled } from 'twin.macro';
import type { Lens, Sequence1DColumn, Vec2 } from '../../types';
import { isSequence1DColumn } from '../../types';
import useSetting from '../useSetting';
import MenuBar from './MenuBar';

const Container = styled.div`
    ${tw`h-full flex flex-col relative items-center w-full`}
`;
const ViewerWrapper = styled.div`
    ${tw`flex flex-grow items-center justify-center h-full w-full`}
`;

const Info = tw.div`flex w-full h-full justify-center items-center text-gray-500 italic text-xs text-center`;

const SequenceView: Lens<Vec2[]> = ({ values, columns, syncKey }) => {
    const [sequences, window] = useMemo(
        () => [
            values.filter((_value, index) => isSequence1DColumn(columns[index])),
            values.find((_value, index) => columns[index].type.kind === 'Window') as
                | [number, number]
                | undefined,
        ],
        [values, columns]
    );

    const chartData = useMemo(() => {
        return sequences
            .filter((v) => v !== null)
            .map((vals, i) => {
                const column = columns[i] as Sequence1DColumn;
                return {
                    values: vals,
                    xLabel: column.xLabel,
                    yLabel: column.yLabel,
                    name: column.name,
                };
            });
    }, [sequences, columns]);

    const chartRef = useRef<LineChartRef>(null);
    const [localXExtents, setLocalXExtents] = useState<Vec2>([-Infinity, Infinity]);

    const categoricalPalette = useColors((c) => c.categoricalPalette);

    const [yAxisMultiple, setYAxisMultiple] = useSetting('yAxisMultiple', false);
    const [xExtents, setXExtents] = useSetting<Vec2>('xExtents', [-Infinity, Infinity]);

    const [isXSynchronized, setIsXSynchronized] = useSetting('isXSynchronized', false);
    const [syncedYDomains, setSyncedYDomains] = useSetting<{
        [key: string]: [number, number];
    }>('syncedYDomains', {});

    // calculate y domains from sliced data
    const calculatedYDomains: [number, number][] = useMemo(
        () =>
            chartData.map(({ values }) => {
                const start = _.sortedIndexBy(
                    values.map(([x]) => x),
                    localXExtents[0]
                );
                const end = Math.max(
                    start + 2,
                    _.sortedIndexBy(
                        values.map(([x]) => x),
                        localXExtents[1]
                    )
                );
                const slice = values.slice(start, end);

                const lowerBound = _.minBy(slice, 1)?.[1] ?? 0;
                const upperBound = _.maxBy(slice, 1)?.[1] ?? 1;
                return [lowerBound, upperBound];
            }) || [],
        [chartData, localXExtents]
    );

    const handleChangeIsYSynchronized = useCallback(
        (isSynchronized: boolean) => {
            if (isSynchronized) {
                const domains: Record<string, [number, number]> = {};
                chartData.forEach(({ name }, index) => {
                    domains[name] = calculatedYDomains[index];
                });
                setSyncedYDomains(domains);
            } else {
                setSyncedYDomains({});
            }
        },
        [chartData, calculatedYDomains, setSyncedYDomains]
    );

    const isYSynchronized = useMemo(
        () =>
            _.every(chartData, ({ name }) => {
                return syncedYDomains[name];
            }),
        [syncedYDomains, chartData]
    );
    const yDomains = useMemo(
        () =>
            chartData.map(({ name }, index) => {
                const key = `${name}`;
                return syncedYDomains[key] ?? calculatedYDomains[index];
            }),
        [syncedYDomains, calculatedYDomains, chartData]
    );

    const chartColors = useMemo(
        () => values.map((_color, i) => categoricalPalette.scale()(i).hex()),
        [values, categoricalPalette]
    );

    const setLocalAndGlobalXAxisExtents = useCallback(
        (ext: Vec2) => {
            if (isXSynchronized) setXExtents(ext);
            setLocalXExtents(ext);
        },
        [isXSynchronized, setXExtents]
    );

    const onChangeIsXSynchronized = useCallback(
        (sync: boolean) => {
            setIsXSynchronized(sync);
            if (sync) {
                setXExtents(localXExtents);
            }
        },
        [setIsXSynchronized, localXExtents, setXExtents]
    );

    const displayedXExtents = useMemo(
        () => (isXSynchronized ? xExtents : localXExtents),
        [isXSynchronized, xExtents, localXExtents]
    );

    const clampedWindows = useMemo(() => {
        if (!window) return [];
        const [start, end] = window;
        return [
            [
                Math.max(start, displayedXExtents[0]),
                Math.min(end, displayedXExtents[1]),
            ],
        ] as [number, number][];
    }, [displayedXExtents, window]);

    const resetPlot = useCallback(() => {
        if (chartRef.current) {
            chartRef.current.reset();
        }
    }, []);

    return (
        <Container>
            {chartData && chartData.length > 0 ? (
                <ViewerWrapper>
                    <LineChart
                        ref={chartRef}
                        chartData={chartData}
                        chartColors={chartColors}
                        multipleYScales={yAxisMultiple}
                        xExtents={displayedXExtents}
                        onChangeXExtents={setLocalAndGlobalXAxisExtents}
                        syncKey={syncKey}
                        yDomains={yDomains}
                        highlightedRegions={clampedWindows}
                    />
                </ViewerWrapper>
            ) : (
                <Info>
                    <span>Empty sequence</span>
                </Info>
            )}

            {
                // Add the menubar as last component, so that it is rendered on top
                // We don't use a z-index for this, because it interferes with the rendering of the contained menus
            }

            <MenuBar
                groupY={yAxisMultiple}
                isXSynchronized={isXSynchronized}
                isYSynchronized={isYSynchronized}
                onChangeGroupY={setYAxisMultiple}
                onReset={resetPlot}
                onChangeIsXSynchronized={onChangeIsXSynchronized}
                onChangeIsYSynchronized={handleChangeIsYSynchronized}
            />
        </Container>
    );
};

SequenceView.key = 'SequenceView';
SequenceView.dataTypes = ['Sequence1D', 'Window'];
SequenceView.multi = true;
SequenceView.defaultHeight = 192;
SequenceView.displayName = 'Lineplot';
SequenceView.minHeight = 45;
SequenceView.multi = true;
SequenceView.filterAllowedColumns = (allColumns, selectedColumns) => {
    // allow max 1 window column
    if (selectedColumns.some((col) => col.type.kind === 'Window'))
        return allColumns.filter((col) => col.type.kind === 'Sequence1D');

    return allColumns.filter((col) => ['Sequence1D', 'Window'].includes(col.type.kind));
};
SequenceView.isSatisfied = (columns) => {
    return columns.some((col) => isSequence1DColumn(col));
};

export default SequenceView;

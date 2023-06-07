import LineChart, { Handle as LineChartRef } from '../../components/LineChart';
import _ from 'lodash';
import { useCallback, useMemo, useRef, useState } from 'react';
import { useColors } from '../../stores/colors';
import tw, { styled } from 'twin.macro';
import type { Sequence1DColumn, Vec2, Lens } from '../../types';
import useSetting from '../useSetting';
import MenuBar from './MenuBar';

const Container = styled.div`
    ${tw`h-full flex flex-col relative items-center w-full`}
`;
const ViewerWrapper = styled.div`
    ${tw`flex flex-grow items-center justify-center h-full w-full`}
`;

const Info = tw.div`flex w-full h-full justify-center items-center text-gray-500 italic text-xs text-center`;

const SequenceView: Lens = ({ values, columns, syncKey }) => {
    const chartData = useMemo(() => {
        const decoder = new TextDecoder();
        return values
            .filter((v) => v !== null)
            .map((buffer, i) => {
                const column = columns[i] as Sequence1DColumn;
                const vals = JSON.parse(decoder.decode(buffer as ArrayBuffer)) as [
                    number,
                    number
                ][];
                return {
                    values: vals,
                    xLabel: column.xLabel,
                    yLabel: column.yLabel,
                    name: column.name,
                };
            });
    }, [values, columns]);

    const chartRef = useRef<LineChartRef>(null);
    const [localXExtents, setLocalXExtents] = useState<Vec2>([-Infinity, Infinity]);

    const categoricalPalette = useColors((c) => c.categoricalPalette);

    const [isXSyncedGlobally, setIsXSyncedGlobally] = useSetting(
        'isXSyncedGlobally',
        false,
        true
    );
    const [yAxisMultiple, setYAxisMultiple] = useSetting('yAxisMultiple', false);
    const [xExtents, setXExtents] = useSetting<Vec2>(
        'xExtents',
        [-Infinity, Infinity],
        isXSyncedGlobally
    );

    const [isXSynchronized, setIsXSynchronized] = useSetting('isXSynchronized', false);
    const [syncedYDomains, setSyncedYDomains] = useSetting<{
        [key: string]: [number, number];
    }>('syncedYDomains', {});

    const syncYDomain = useCallback(
        (key: string, domain: [number, number]) => {
            setSyncedYDomains((domains) => ({
                ...domains,
                [key]: domain,
            }));
        },
        [setSyncedYDomains]
    );
    const unsyncYDomain = useCallback(
        (key: string) => {
            setSyncedYDomains((domains) => _.omit(domains, key));
        },
        [setSyncedYDomains]
    );

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
            chartData.forEach(({ name }, index) => {
                const key = `${syncKey}_${name}`;

                if (isSynchronized) {
                    syncYDomain(key, calculatedYDomains[index]);
                } else {
                    unsyncYDomain(key);
                }
            });
        },
        [chartData, calculatedYDomains, syncYDomain, unsyncYDomain, syncKey]
    );

    const isYSynchronized = useMemo(
        () =>
            _.every(chartData, ({ name }) => {
                const key = `${syncKey}_${name}`;
                return syncedYDomains[key];
            }),
        [syncedYDomains, syncKey, chartData]
    );

    const yDomains = useMemo(
        () =>
            chartData.map(({ name }, index) => {
                const key = `${syncKey}_${name}`;
                return syncedYDomains[key] ?? calculatedYDomains[index];
            }),
        [syncedYDomains, calculatedYDomains, chartData, syncKey]
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
                isXSyncedGlobally={isXSyncedGlobally}
                onChangeGroupY={setYAxisMultiple}
                onReset={resetPlot}
                onChangeIsXSynchronized={onChangeIsXSynchronized}
                onChangeIsYSynchronized={handleChangeIsYSynchronized}
                onChangeIsXSyncedGlobally={setIsXSyncedGlobally}
            />
        </Container>
    );
};

SequenceView.key = 'SequenceView';
SequenceView.dataTypes = ['Sequence1D'];
SequenceView.multi = true;
SequenceView.defaultHeight = 192;
SequenceView.displayName = 'Lineplot';
SequenceView.minHeight = 45;

export default SequenceView;

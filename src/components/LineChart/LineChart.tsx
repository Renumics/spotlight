import { useFormatter } from '../../dataformat';
import _ from 'lodash';
import * as React from 'react';
import { forwardRef, useCallback, useImperativeHandle, useMemo, useState } from 'react';
import {
    Legend,
    Line,
    LineChart as RechartLineChart,
    ReferenceArea,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';
import tw, { styled } from 'twin.macro';
import { Vec2 } from '../../types';
import { largestTriangleThreeBuckets } from '../../math/downsampling';

const Info = tw.div`flex w-full h-full justify-center items-center text-gray-500 italic text-xs text-center`;

const LineChartStyleWrapper = styled.div`
    ${tw`w-full h-full`}
    g.highlighted-region path {
        ${tw`fill-blue-500 stroke-0 opacity-30 hover:opacity-50`}
    }
`;

type Domain = [number, number];
export type Series = { name: string; values: Vec2[]; xLabel?: string; yLabel?: string };
export type LineChartProps = {
    chartData: Series[];
    highlightedRegions?: [number, number][];
    multipleYScales?: boolean;
    chartColors?: string[];
    xExtents?: Vec2;
    onChangeXExtents?: (ext: Vec2) => void;
    syncKey?: string;
    yDomains?: Domain[];
};

export interface Handle {
    reset: () => void;
}

const closestIndexToLabel = (
    label: number,
    series: [number, number][]
): [number, number] | undefined => {
    // if label is outside of series return undefined
    if (label > series[series.length - 1][0] || label < series[0][0]) return undefined;

    const high = _.sortedIndexBy(series, [label, 0], (l) => l[0]);
    const low = high - 1;

    const highValue = series[high];
    const lowValue = series[low];

    if (highValue === undefined) return lowValue;
    if (lowValue === undefined) return highValue;

    if (Math.abs(highValue[0] - label) < Math.abs(lowValue[0] - label))
        return highValue;
    return lowValue;
};

const Bubble = tw.div`bg-gray-100 border rounded shadow select-none z-20 relative px-2 py-2`;

const TooltipContent: React.FunctionComponent<{
    chartData: Series[];
    chartColors: string[];
    label?: number;
}> = (props) => {
    const { chartData, chartColors, label } = props;

    const payload = useMemo(() => {
        return chartData
            .map((data, index) => ({
                name: data.name,
                color: chartColors[index],
                data: closestIndexToLabel(label ?? 0, data.values),
                yLabel: data.yLabel,
            }))
            .filter(({ data }) => data !== undefined);
    }, [chartData, label, chartColors]);

    const xLabel = useMemo(() => {
        return chartData.every((data) => data.xLabel === chartData[0]?.xLabel)
            ? chartData[0]?.xLabel
            : undefined;
    }, [chartData]);

    const dataformat = useFormatter();

    return (
        <Bubble>
            <div>
                {dataformat.formatFloat(label ?? 0)} {xLabel}
            </div>
            {payload.map((p, index) => {
                if (!p.data?.[1]) return null;
                return (
                    <div key={index} tw="flex" style={{ color: p.color }}>
                        <div tw="flex-grow mr-2">{p.name}</div>
                        <div>
                            {dataformat.formatFloat(p.data[1])} {p.yLabel}
                        </div>
                    </div>
                );
            })}
        </Bubble>
    );
};

const CustomTooltip: React.FunctionComponent<{
    chartData: Series[];
    chartColors: string[];
    label?: number;
    active?: boolean;
}> = ({ active, ...contentProps }) => {
    if (!active) return <></>;
    return <TooltipContent {...contentProps} />;
};

const DEFAULT_CHART_COLORS = ['black'];
const DEFAULT_X_EXTENTS = [-Infinity, Infinity];
const DEFAULT_Y_DOMAINS = [] as Domain[];

const LineChart: React.ForwardRefRenderFunction<Handle, LineChartProps> = (
    {
        chartData,
        chartColors = DEFAULT_CHART_COLORS,
        multipleYScales,
        xExtents = DEFAULT_X_EXTENTS,
        onChangeXExtents,
        syncKey,
        yDomains = DEFAULT_Y_DOMAINS,
        highlightedRegions = [],
    },
    ref
) => {
    const [refAreaLeft, setRefAreaLeft] = useState<number | undefined>();
    const [refAreaRight, setRefAreaRight] = useState<number | undefined>();

    const data = useMemo(() => {
        if (chartData)
            return chartData.map(({ name, values }) => {
                const start = _.sortedIndexBy(
                    values.map(([x]) => x),
                    xExtents[0]
                );
                const end = Math.max(
                    start + 2,
                    _.sortedIndexBy(
                        values.map(([x]) => x),
                        xExtents[1]
                    )
                );
                return {
                    name,
                    values: largestTriangleThreeBuckets(
                        values.slice(start, end),
                        100
                    ).map(([x, y]) => ({
                        name: x,
                        y,
                    })),
                };
            });
        return [];
    }, [chartData, xExtents]);

    const [xLabels, yLabels] = useMemo(
        () => [
            _.uniq(chartData.map((v) => v.xLabel)),
            _.uniq(chartData.map((v) => v.yLabel)),
        ],
        [chartData]
    );

    const xAxisLabel = useMemo(
        () => ({
            value: xLabels.join(', '),
            position: 'insideBottomRight',
            offset: 0,
        }),
        [xLabels]
    );

    const yAxisLabel = useMemo(
        () => ({
            value: yLabels.join(', '),
            position: 'insideTopLeft',
            angle: -90,
        }),
        [yLabels]
    );

    const yAxisLabels = useMemo(
        () =>
            yLabels.map((label) => ({
                value: label,
                position: 'insideTopLeft',
                angle: -90,
            })),
        [yLabels]
    );

    // without show multiple we combine y-domains by choosing
    // the min and max over all individual domains
    const combinedYDomain = useMemo(
        () =>
            yDomains.reduce(
                (combined, domain) => {
                    combined[0] = Math.min(domain[0], combined[0]);
                    combined[1] = Math.max(domain[1], combined[1]);
                    return combined;
                },
                [Infinity, -Infinity]
            ),
        [yDomains]
    );

    useImperativeHandle(ref, () => ({
        reset: () => {
            onChangeXExtents?.([-Infinity, Infinity]);
        },
    }));

    const zoom = useCallback(() => {
        if (refAreaLeft && refAreaRight) {
            const min = Math.min(refAreaLeft, refAreaRight);
            const max = Math.max(refAreaLeft, refAreaRight);
            onChangeXExtents?.([min, max]);
        }
        setRefAreaLeft(undefined);
    }, [refAreaLeft, refAreaRight, onChangeXExtents]);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const lineChartMouseDown = useCallback((e: any) => {
        if (e) setRefAreaLeft(e.activeLabel);
    }, []);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const lineChartMouseMove = useCallback((chartState: any, e: MouseEvent) => {
        if (e.buttons === 1) setRefAreaRight(chartState.activeLabel);
    }, []);

    const dataformat = useFormatter();

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const formatter = useCallback(
        (value: any) => {
            if (typeof value === 'number') {
                return dataformat.formatFloat(value);
            } else {
                return value.toString();
            }
        },
        [dataformat]
    );

    const xDomain = useMemo(() => ['dataMin', 'dataMax'], []);
    const allowEscapeViewBox = useMemo(() => ({ x: false, y: false }), []);
    const tooltipWrapperStyle = useMemo(() => ({ zIndex: 40 }), []);
    const legendWrapperStyle = useMemo(
        () => ({
            ...tw`text-xxs pb-1`,
        }),
        []
    );

    if (!data.some(({ values }) => values.length > 0)) {
        return (
            <Info>
                <span>
                    No Data in Range ({dataformat.formatFloat(xExtents[0])},{' '}
                    {dataformat.formatFloat(xExtents[1])})
                </span>
            </Info>
        );
    }
    return (
        <LineChartStyleWrapper>
            <ResponsiveContainer tw="text-xxs" width="100%" height="100%" debounce={1}>
                <RechartLineChart
                    data={data}
                    onMouseDown={lineChartMouseDown}
                    onMouseMove={lineChartMouseMove}
                    syncId={syncKey}
                    onMouseUp={zoom}
                    margin={{ top: 4, right: 4, left: 4, bottom: 4 }}
                >
                    <Tooltip
                        allowEscapeViewBox={allowEscapeViewBox}
                        wrapperStyle={tooltipWrapperStyle}
                        labelFormatter={formatter}
                        formatter={formatter}
                        isAnimationActive={false}
                        content={
                            <CustomTooltip
                                chartData={chartData}
                                chartColors={chartColors}
                            />
                        }
                    />
                    <Legend verticalAlign="top" wrapperStyle={legendWrapperStyle} />
                    <XAxis
                        xAxisId={0}
                        label={xAxisLabel}
                        dataKey="name"
                        height={12}
                        type="number"
                        tickFormatter={formatter}
                        domain={xDomain}
                        allowDataOverflow={true}
                        // needs dict like data format in order to function properly therefore diable it
                        allowDuplicatedCategory={false}
                    />
                    {multipleYScales ? (
                        data.map((_d, index) => (
                            <YAxis
                                width={32}
                                label={yAxisLabels}
                                key={index}
                                yAxisId={index}
                                type="number"
                                domain={yDomains[index]}
                                tickFormatter={formatter}
                                allowDataOverflow={true}
                                stroke={chartColors[index] || chartColors[0]}
                            />
                        ))
                    ) : (
                        <YAxis
                            width={32}
                            yAxisId={0}
                            type="number"
                            label={yAxisLabel}
                            domain={combinedYDomain}
                            tickFormatter={formatter}
                            allowDataOverflow={true}
                        />
                    )}
                    {data.map(({ name, values }, index) => (
                        <Line
                            yAxisId={multipleYScales ? index : 0}
                            xAxisId={0}
                            type="monotone"
                            dataKey="y"
                            data={values}
                            name={name}
                            key={name}
                            dot={false}
                            activeDot={false}
                            stroke={chartColors[index] || chartColors[0]}
                            animationDuration={100}
                        />
                    ))}
                    {refAreaLeft && refAreaRight && (
                        <ReferenceArea
                            x1={refAreaLeft}
                            x2={refAreaRight}
                            strokeOpacity={0.3}
                        />
                    )}
                    {highlightedRegions?.map(([start, end], index) => (
                        <ReferenceArea
                            key={index}
                            x1={start}
                            x2={end}
                            className="highlighted-region"
                        />
                    ))}
                </RechartLineChart>
            </ResponsiveContainer>
        </LineChartStyleWrapper>
    );
};

export default forwardRef(LineChart);

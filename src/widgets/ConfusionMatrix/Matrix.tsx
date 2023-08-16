import 'twin.macro';
import * as d3 from 'd3';
import useSize from '../../hooks/useSize';
import { useMemo, useRef } from 'react';
import { useColors } from '../../lib';

interface Props {
    data: MatrixData;
}

const MARGIN = {
    right: 8,
    top: 8,
    left: 18,
    bottom: 18,
};

const Matrix = ({ data }: Props): JSX.Element => {
    const wrapperRef = useRef<HTMLDivElement>(null);
    const { width, height } = useSize(wrapperRef);

    const boundsWidth = width - MARGIN.left - MARGIN.right;
    const boundsHeight = height - MARGIN.top - MARGIN.bottom;

    const xScale = useMemo(
        () => d3.scaleBand().range([0, boundsWidth]).domain(data.xNames).padding(0.01),
        [data.xNames, boundsWidth]
    );

    const yScale = useMemo(
        () => d3.scaleBand().range([0, boundsHeight]).domain(data.yNames).padding(0.01),
        [data.yNames, boundsHeight]
    );

    const [min, max] = useMemo(() => {
        const counts = data.buckets.map((b) => b.rows.length);
        return d3.extent(counts);
    }, []);
    const colorScale = useColors((state) => state.continuousPalette)
        .scale()
        .domain([min ?? 0, max ?? 1]);

    const rows = data.xNames.length;
    const rects = data.buckets.map((bucket, i) => (
        <g key={i}>
            <rect
                x={xScale(data.xNames[i % rows])}
                y={yScale(data.yNames[(i / rows) >> 0])}
                width={xScale.bandwidth()}
                height={yScale.bandwidth()}
                fill={colorScale(bucket.rows.length).css()}
                rx={8}
                stroke={'white'}
            />
            <text
                x={(xScale(data.xNames[i % rows]) ?? 0) + xScale.bandwidth() / 2}
                y={(yScale(data.yNames[(i / rows) >> 0]) ?? 0) + yScale.bandwidth() / 2}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={10}
                fontWeight="bold"
            >
                {data.buckets[i].rows.length > 0 ? data.buckets[i].rows.length : ''}
            </text>
        </g>
    ));

    const xLabels = data.xNames.map((name, i) => (
        <text
            key={i}
            x={(xScale(name) ?? 0) + xScale.bandwidth() / 2}
            y={boundsHeight + 8}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={10}
        >
            {name}
        </text>
    ));

    const yLabels = data.yNames.map((name, i) => (
        <text
            key={i}
            x={-4}
            y={(yScale(name) ?? 0) + yScale.bandwidth() / 2}
            textAnchor="end"
            dominantBaseline="middle"
            fontSize={10}
        >
            {name}
        </text>
    ));

    return (
        <div tw="w-full h-full overflow-hidden" ref={wrapperRef}>
            <svg width={width} height={height}>
                <g
                    width={boundsWidth}
                    height={boundsHeight}
                    transform={`translate(${MARGIN.left},${MARGIN.top})`}
                >
                    {rects}
                    {xLabels}
                    {yLabels}
                </g>
            </svg>
        </div>
    );
};

export default Matrix;

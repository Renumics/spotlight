import 'twin.macro';
import * as d3 from 'd3';
import useSize from '../../hooks/useSize';
import { useMemo, useRef } from 'react';

interface Props {
    xNames: string[];
    yNames: string[];
    data: number[];
}

const MARGIN = {
    right: 8,
    top: 8,
    left: 18,
    bottom: 18,
};

const Matrix = ({ xNames, yNames, data }: Props): JSX.Element => {
    const wrapperRef = useRef<HTMLDivElement>(null);
    const { width, height } = useSize(wrapperRef);

    const boundsWidth = width - MARGIN.left - MARGIN.right;
    const boundsHeight = height - MARGIN.top - MARGIN.bottom;

    const xScale = useMemo(
        () => d3.scaleBand().range([0, boundsWidth]).domain(xNames).padding(0.01),
        [xNames, boundsWidth]
    );

    const yScale = useMemo(
        () => d3.scaleBand().range([0, boundsHeight]).domain(yNames).padding(0.01),
        [yNames, boundsHeight]
    );

    const [min, max] = d3.extent(data);
    const colorScale = d3
        .scaleSequential()
        .interpolator(d3.interpolateInferno)
        .domain([min ?? 0, max ?? 1]);

    const rows = xNames.length;
    const rects = data.map((value, i) => (
        <rect
            key={i}
            x={xScale(xNames[i % rows])}
            y={yScale(yNames[(i / rows) >> 0])}
            width={xScale.bandwidth()}
            height={yScale.bandwidth()}
            fill={colorScale(value)}
            opacity={1}
            rx={8}
            stroke={'white'}
        />
    ));

    const xLabels = xNames.map((name, i) => (
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

    const yLabels = yNames.map((name, i) => (
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

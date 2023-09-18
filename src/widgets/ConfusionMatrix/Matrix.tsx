import * as d3 from 'd3';
import useSize from '../../hooks/useSize';
import { useMemo, useRef } from 'react';
import { useColors } from '../../lib';
import type { Cell, MatrixData } from './types';
import { theme } from 'twin.macro';

interface Props {
    data: MatrixData;
    onHoverCell?: (cell?: Cell) => void;
    onClickCell?: (cell?: Cell) => void;
}

const MARGIN = {
    right: 8,
    top: 8,
    left: 18,
    bottom: 18,
};

const Matrix = ({ data, onHoverCell, onClickCell }: Props): JSX.Element => {
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
    }, [data.buckets]);
    const colorScale = useColors((state) => state.continuousPalette)
        .scale()
        .domain([min ?? 0, max ?? 1]);

    const rects = data.buckets.map((bucket, i) => {
        const rows = data.xNames.length;
        const col = i % rows;
        const row = (i / rows) >> 0;
        const left = xScale(data.xNames[col]) ?? 0;
        const top = yScale(data.yNames[row]) ?? 0;

        const bgColor = colorScale(bucket.rows.length);
        const isBgDark = bgColor.get('oklab.l') < 0.5;
        const fgColorCss = isBgDark ? theme`colors.white` : theme`colors.black`;

        return (
            <g
                key={i}
                onMouseEnter={(e) => {
                    d3.select(e.currentTarget).select('rect').style('stroke-width', 5);
                    onHoverCell?.({ x: col, y: row, bucket });
                }}
                onMouseLeave={(e) => {
                    d3.select(e.currentTarget).select('rect').style('stroke-width', 0);
                    onHoverCell?.(undefined);
                }}
                onClick={() => onClickCell?.({ x: col, y: row, bucket })}
                cursor="pointer"
            >
                <rect
                    x={left}
                    y={top}
                    width={xScale.bandwidth()}
                    height={yScale.bandwidth()}
                    fill={bgColor.css()}
                    rx={5}
                    stroke={theme`colors.white`}
                />
                <text
                    x={left + xScale.bandwidth() / 2}
                    y={top + yScale.bandwidth() / 2}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={12}
                    fill={fgColorCss}
                    fontWeight="bold"
                >
                    {data.buckets[i].rows.length}
                </text>
            </g>
        );
    });

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
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={10}
            transform={`translate(${-4}, ${
                (yScale(name) ?? 0) + yScale.bandwidth() / 2
            }) rotate(-90)`}
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

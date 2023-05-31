import * as d3 from 'd3';
import _ from 'lodash';
import { useEffect, useRef } from 'react';
import { theme } from 'twin.macro';
import { Bin, HistogramData } from './types';

const MAX_DISCRETE_BINS_TO_RENDER_TICKS = 25;

const truncateText = (node: SVGTextElement | null, width: number) => {
    if (!node) return;

    const selection = d3.select(node);

    let textLength = selection.node()?.getComputedTextLength() ?? 0;
    let text = selection.text();
    while (textLength > width && text.length > 0) {
        text = text.slice(0, -1);
        selection.text(text + '...');
        textLength = selection.node()?.getComputedTextLength() ?? 0;
    }
};

interface FactoryProps {
    width: number;
    height: number;
    histogram: HistogramData;
    hideUnfiltered: boolean;
}

interface Props {
    width: number;
    height: number;
    xBins: Bin[];
}

const YPAD = 1;

const DiscreteXAxis = ({ width, height, xBins }: Props): JSX.Element => {
    const ref = useRef<SVGGElement>(null);

    useEffect(() => {
        if (!ref.current) return;

        const xAxisHeight = 14;
        const xScale = d3
            .scaleBand(d3.range(xBins.length), [0, width])
            .padding(0)
            .round(true);

        const xAxis = d3
            .axisBottom(xScale)
            .tickSizeOuter(0)
            .tickSizeInner(0)
            .tickFormat((d) => `${xBins[d].key}`);

        const group = d3.select<SVGGElement, unknown>(ref.current);

        group.attr('transform', `translate(0,${height - xAxisHeight})`).call(xAxis);

        group.selectAll('path.domain').style('color', theme`colors.gray.400`);
        group.selectAll('g.tick').style('color', theme`colors.midnight.500`);
        group
            .selectAll('g.tick')
            .select<SVGTextElement>('text')
            .each((_, i, nodes) => truncateText(nodes[i], xScale.bandwidth() - YPAD));
    }, [width, height, xBins]);

    return (
        <>
            <g ref={ref} />
        </>
    );
};

const ContinuousXAxis = ({ width, height, xBins }: Props): JSX.Element => {
    const ref = useRef<SVGGElement>(null);

    useEffect(() => {
        if (!ref.current) return;

        const xAxisHeight = 14;

        const xScale = d3
            .scaleLinear()
            .domain([_.minBy(xBins, 'min')?.min || 0, _.maxBy(xBins, 'max')?.max || 0])
            .range([0, width]);

        const xAxis = d3
            .axisBottom(xScale)
            .tickSizeOuter(0)
            .tickSizeInner(2)
            .tickPadding(2);

        const group = d3.select<SVGGElement, unknown>(ref.current);

        group.attr('transform', `translate(0,${height - xAxisHeight})`).call(xAxis);

        group.selectAll('path.domain').style('color', theme`colors.gray.600`);

        group.selectAll('g.tick > line').style('color', theme`colors.gray.600`);

        group
            .selectAll('g.tick > text')
            .style('color', theme`colors.midnight.500`)
            .style('text-anchor', 'middle');

        group
            .select('g.tick:first-of-type > text')
            .style('text-anchor', 'start')
            .attr('x', 2);
        group
            .select('g.tick:last-of-type > text')
            .style('text-anchor', 'end')
            .attr('x', -2);
    }, [width, height, xBins]);

    return <g ref={ref} />;
};

const XAxis = (props: FactoryProps): JSX.Element => {
    const { width, height, histogram, hideUnfiltered } = props;

    const xBins = hideUnfiltered
        ? histogram.xBins.filter(({ key }) =>
              histogram.filtered[histogram.filtered.length - 1]
                  .map(({ xKey }) => xKey)
                  .includes(key)
          )
        : histogram.xBins;
    switch (props.histogram.kind) {
        case 'discrete':
            if (xBins.length > MAX_DISCRETE_BINS_TO_RENDER_TICKS) return <></>;
            return <DiscreteXAxis width={width} height={height} xBins={xBins} />;
        case 'continuous':
            return <ContinuousXAxis width={width} height={height} xBins={xBins} />;
    }
};

export default XAxis;

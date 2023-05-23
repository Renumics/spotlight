import * as d3 from 'd3';
import { formatNumber } from '../../../dataformat';
import { FunctionComponent, useContext, useEffect } from 'react';
import { theme } from 'twin.macro';
import PlotContext from './PlotContext';

interface Props {
    caption?: string;
}

function findOrCreateGroup<P extends SVGElement>(parentElement: P) {
    const parent = d3.select<P, unknown>(parentElement);
    const selection = parent.select<SVGGElement>('g.yaxis');
    if (selection.empty()) {
        const g = parent.append('g').classed('yaxis', true);
        g.append('g').classed('axis', true);
        g.append('text').classed('caption', true);
        return g;
    }
    return selection;
}

const YAxis: FunctionComponent<Props> = ({ caption }) => {
    const { transform, svgRef, width, height, yScale } = useContext(PlotContext);

    useEffect(() => {
        if (!transform || !svgRef.current) return;

        const group = findOrCreateGroup(svgRef.current);

        const axis = d3
            .axisLeft(
                d3
                    .scaleLinear()
                    .range([height - 32, 10])
                    .domain([
                        yScale.invert(transform.invertY(height - 32)),
                        yScale.invert(transform.invertY(10)),
                    ])
            )
            .ticks(height / 64)
            .tickSizeOuter(0)
            .tickFormat((value) => formatNumber(value as number));

        group.style('font-size', '0.75rem');
        group.style('color', theme`colors.gray.900`);
        group.select<SVGGElement>('g.axis').call(axis);

        group
            .selectAll('path.domain')
            .attr('d', `M0,0H14V${height}H0`)
            .style('stroke-width', 1)
            .attr('fill', theme`colors.gray.100`)
            .attr('stroke', theme`colors.gray.600`);
        group
            .selectAll('.tick line')
            .style('stroke-width', 1)
            .attr('stroke', theme`colors.gray.600`)
            .attr('x1', 0)
            .attr('x2', 14);
        group.selectAll('.tick text').attr('x', 18).attr('text-anchor', 'start');

        group
            .select('.caption')
            .attr('transform', 'translate(4, 3), rotate(90)')
            .attr('font-size', '0.75rem')
            .attr('font-weight', 'bold')
            .attr('color', theme`colors.midnight.600`)
            .attr('text-anchor', 'start')
            .text(caption ?? '');
    }, [transform, svgRef, width, height, yScale, caption]);

    return <></>;
};

export default YAxis;

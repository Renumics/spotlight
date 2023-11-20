import * as d3 from 'd3';
import { useFormatter } from '../../../dataformat';
import { FunctionComponent, useContext, useEffect } from 'react';
import { theme } from 'twin.macro';
import PlotContext from './PlotContext';

interface Props {
    caption?: string;
}

function findOrCreateGroup<P extends SVGElement>(parentElement: P) {
    const parent = d3.select<P, unknown>(parentElement);
    const selection = parent.select<SVGGElement>('g.xaxis');
    if (selection.empty()) {
        const g = parent.append('g').classed('xaxis', true);
        g.append('g').classed('axis', true);
        g.append('text').classed('caption', true);
        return g;
    }
    return selection;
}

const XAxis: FunctionComponent<Props> = ({ caption }) => {
    const { transform, svgRef, width, height, xScale } = useContext(PlotContext);

    const formatter = useFormatter();

    useEffect(() => {
        if (!transform || !svgRef.current) return;

        const group = findOrCreateGroup(svgRef.current);

        const xAxis = d3
            .axisBottom(
                d3
                    .scaleLinear()
                    .range([20, width - 10])
                    .domain([
                        xScale.invert(transform.invertX(20)),
                        xScale.invert(transform.invertX(width - 10)),
                    ])
            )
            .ticks(width / 64)
            .tickSizeOuter(0)
            .tickFormat((value) => formatter.formatFloat(value as number));

        group.attr('transform', `translate(0, ${height})`);
        group.style('font-size', '0.75rem');
        group.style('color', theme`colors.gray.900`);
        group.select<SVGGElement>('g.axis').call(xAxis);

        group
            .selectAll('path.domain')
            .attr('d', `M0,0V-14H${width}V0`)
            .style('stroke-width', 1)
            .attr('fill', theme`colors.gray.100`)
            .attr('stroke', theme`colors.gray.600`);
        group
            .selectAll('.tick line')
            .style('stroke-width', 1)
            .attr('stroke', theme`colors.gray.600`)
            .attr('y1', 0)
            .attr('y2', -14);
        group.selectAll('.tick text').attr('y', -26);

        group
            .select('.caption')
            .attr('transform', `translate(${width - 3}, -3)`)
            .attr('font-size', '0.75rem')
            .attr('font-weight', 'bold')
            .attr('color', theme`colors.midnight.600`)
            .attr('text-anchor', 'end')
            .text(caption ?? '');
    }, [transform, svgRef, width, height, xScale, caption, formatter]);

    return <></>;
};

export default XAxis;

import { Color } from 'chroma-js';
import * as d3 from 'd3';
import { useFormatter } from '../../../../dataformat';
import { ContinuousTransferFunction } from '../../../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { useEffect, useMemo, useRef, useState } from 'react';
import tw, { styled } from 'twin.macro';
import { CategoricalLegend } from './CategoricalLegend';
import {
    Alignment,
    Arrangement,
    DEFAULT_ALIGNMENT,
    DEFAULT_ARRANGEMENT,
} from './index';

export interface ContinuousProps {
    steps: Color[];
    domain: [number, number];
    arrange?: Arrangement;
    align?: Alignment;
}

const ContinuousLegendWrapper = styled.div(
    ({ arrange, align }: { arrange: Arrangement; align: Alignment }) => [
        tw`w-full flex`,
        arrange === 'vertical' && tw`w-20 flex-row`,
        align === 'center' && tw`self-center`,
        align === 'right' && tw`self-end`,
        align === 'left' && tw`self-start`,
        align === 'left' && arrange === 'vertical' && tw`flex-row-reverse`,
        arrange === 'horizontal' && tw`flex-col-reverse space-y-1`,
    ]
);

const ContinuousLegendSVGWrapper = styled.svg(
    ({ arrange }: { arrange: Arrangement }) => [
        tw`ml-2 mr-2`,
        arrange === 'horizontal' && tw`h-3`,
        arrange === 'vertical' && tw`h-32 w-5`,
    ]
);

const ContinuousLegendAnnotationWrapper = styled.div(
    ({ arrange }: { arrange?: Arrangement }) => [
        tw`w-full text-gray-900 text-xs flex place-content-between`,
        arrange === 'vertical' && tw`flex-col`,
    ]
);

export const ContinuousLegend = ({
    align = DEFAULT_ALIGNMENT,
    arrange = DEFAULT_ARRANGEMENT,
    steps,
    domain,
}: ContinuousProps): JSX.Element => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [gradientID] = useState(_.uniqueId('gradient_'));

    useEffect(() => {
        const gradient = d3.select(`linearGradient#${gradientID}`);
        gradient.selectAll('*').remove();
        steps.forEach((val, index) => {
            gradient
                .append('stop')
                .attr('offset', `${index * (100 / steps.length)}%`)
                .style('stop-color', val.hex()) // end in red
                .style('stop-opacity', 1);
        });
    }, [domain, gradientID, steps]);

    const dataformat = useFormatter();

    return (
        <ContinuousLegendWrapper arrange={arrange} align={align}>
            <ContinuousLegendAnnotationWrapper arrange={arrange}>
                <span style={{ textAlign: align }}>
                    {dataformat.formatFloat(domain[0])}
                </span>
                <span style={{ textAlign: align }}>
                    {dataformat.formatFloat(domain[1])}
                </span>
            </ContinuousLegendAnnotationWrapper>
            <ContinuousLegendSVGWrapper arrange={arrange} ref={svgRef}>
                <linearGradient
                    id={gradientID}
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="0%"
                    gradientTransform={`rotate(${arrange === 'horizontal' ? 0 : 90})`}
                />
                <rect
                    x="0"
                    y="0"
                    width="100%"
                    height="100%"
                    fill={`url(#${gradientID})`}
                />
            </ContinuousLegendSVGWrapper>
        </ContinuousLegendWrapper>
    );
};

interface ContinuousTransferFunctionLegendProps
    extends Omit<ContinuousProps, 'steps' | 'domain'> {
    transferFunction: ContinuousTransferFunction;
}

export const ContinuousTransferFunctionLegend = ({
    transferFunction,
    ...props
}: ContinuousTransferFunctionLegendProps): JSX.Element => {
    const domain = transferFunction.domain;

    const steps = useMemo(() => {
        const numSteps = 50;
        const valSteps = _.range(
            domain[0],
            domain[1],
            (domain[1] - domain[0]) / numSteps
        );

        if (valSteps.length === 0) {
            // if domain[0] === domain[1] the _.range call will return an empty list
            // to counteract that add domain[0] to the list
            valSteps.push(domain[0]);
        }
        return valSteps.map((v) => transferFunction(v));
    }, [domain, transferFunction]);

    const dataformat = useFormatter();

    const classBreaksColorMap = useMemo(() => {
        if (transferFunction.classBreaks === undefined) return undefined;

        return transferFunction.classBreaks.slice(1).map((v, i) => {
            const start = transferFunction.classBreaks?.[i] || 0;
            const end = v;
            return {
                label: `${dataformat.formatFloat(start)} - ${dataformat.formatFloat(
                    end
                )}`,
                color: transferFunction((start + end) / 2),
            };
        });
    }, [transferFunction, dataformat]);

    if (classBreaksColorMap !== undefined) {
        return <CategoricalLegend colorMap={classBreaksColorMap} {...props} />;
    }

    return <ContinuousLegend steps={steps} domain={domain} {...props} />;
};

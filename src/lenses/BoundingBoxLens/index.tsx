import useResizeObserver from '@react-hook/resize-observer';
import { useRef, useEffect } from 'react';
import tw, { styled } from 'twin.macro';
import { Lens } from '../../types';
import { ColorsState, useColors } from '../../stores/colors';
import * as d3 from 'd3';

const StyledContainer = styled.div`
    ${tw`relative inline-block h-full w-full`};
    img {
        ${tw`block h-full w-full`}
    }
    svg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
`;

const BoundingBoxLens: Lens = ({ urls, values }) => {
    const container = useRef<HTMLDivElement>(null);
    const svgRef = useRef<SVGSVGElement>(null);
    const imgRef = useRef<HTMLImageElement>(null);

    const boxes = values[1] as [[number, number, number, number]];
    const categories = values[2] as [number];

    const colorPaletteSelector = (c: ColorsState) => c.continuousPalette;
    const colorPalette = useColors(colorPaletteSelector);

    useResizeObserver(container.current, () => drawBoundingBoxes());
    useEffect(() => drawBoundingBoxes());

    const drawBoundingBoxes = () => {
        if (!svgRef.current) return;
        if (!container.current) return;
        if (!imgRef.current) return;

        // Remove previous svg elements to prevent stacking
        d3.select(svgRef.current).select<SVGSVGElement>('g').selectAll('rect').remove();
        d3.select(svgRef.current).select<SVGSVGElement>('g').selectAll('text').remove();

        const colorScale = colorPalette.scale().colors(boxes.length);
        const w: number = container.current.clientWidth;
        const h: number = container.current.clientHeight;

        for (let i = 0; i < boxes.length; i++) {
            const box = boxes[i];

            // Box format [x, y, w, h] normalized.
            const x = box[0] * w;
            const y = box[1] * h;
            const width = (box[2] - box[0]) * w;
            const height = (box[3] - box[1]) * h;

            d3.select(svgRef.current)
                .select<SVGSVGElement>('g')
                .append('rect')
                .attr('x', x)
                .attr('y', y)
                .attr('width', width)
                .attr('height', height)
                .attr('stroke', 'firebrick')
                .attr('stroke-width', 2)
                .attr('stroke', colorScale[i])
                .attr('fill', 'none');

            if (categories) {
                d3.select(svgRef.current)
                    .select<SVGSVGElement>('g')
                    .append('text')
                    .text(categories[i].toString())
                    .attr('x', boxes[i][0] * w)
                    .attr('y', boxes[i][1] * h - 3)
                    .attr('fontsize', 12)
                    .attr('fill', 'red');
            }
        }
    };

    return (
        <div tw="h-full w-full">
            <StyledContainer ref={container}>
                <img ref={imgRef} src={urls[0]} alt="Not found." />
                <svg ref={svgRef}>
                    <g />
                </svg>
            </StyledContainer>
        </div>
    );
};

BoundingBoxLens.key = 'BoundingBoxView';
BoundingBoxLens.dataTypes = ['Image', 'BoundingBox', 'Sequence'];
BoundingBoxLens.multi = true;
BoundingBoxLens.displayName = 'BoundingBox';
BoundingBoxLens.defaultHeight = 256;

export default BoundingBoxLens;

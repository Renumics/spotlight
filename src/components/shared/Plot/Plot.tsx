import * as d3 from 'd3';
import useSize from '../../../hooks/useSize';
import { useCallback, useMemo, useRef, useState } from 'react';
import tw from 'twin.macro';
import PlotContext from './PlotContext';
import { Point2d } from './types';

interface Props {
    points: Point2d[];
    scaleUniform?: boolean;
    children: JSX.Element[] | JSX.Element;
    isPointHighlighted: (index: number) => boolean;
    setHighlightedPoint: (index: number | undefined) => void;
}

const margin = {
    left: 42,
    right: 20,
    top: 20,
    bottom: 36,
};

const Wrapper = tw.div`relative w-full h-full`;

const Plot = ({
    points,
    isPointHighlighted,
    setHighlightedPoint,
    scaleUniform = false,
    children,
}: Props): JSX.Element => {
    const [canvas, setCanvas] = useState<HTMLCanvasElement | null>(null);
    const svgRef = useRef<SVGSVGElement>(null);
    const transformRef = useRef<d3.ZoomTransform>(d3.zoomIdentity);
    const [zoom] = useState(() => d3.zoom());
    const [xScale, setXScale] = useState<d3.ScaleLinear<number, number>>(() =>
        d3.scaleLinear().domain([0, 1]).range([0, 1])
    );
    const [yScale, setYScale] = useState<d3.ScaleLinear<number, number>>(() =>
        d3.scaleLinear().domain([0, 1]).range([0, 1])
    );
    const [hoveredIndex, setStoredHoveredIndex] = useState<number | undefined>();
    const setHoveredIndex = useCallback(
        (index: number | undefined) => {
            if (index === undefined) {
                setHighlightedPoint(index);
                setStoredHoveredIndex(index);
            } else {
                setStoredHoveredIndex(index);
                setHighlightedPoint(index);
            }
        },
        [setHighlightedPoint]
    );
    const [active, setActive] = useState<boolean>(false);

    const [transform, setTransform] = useState(() => d3.zoomIdentity);

    const wrapperRef = useRef<HTMLDivElement>(null);
    const { width, height } = useSize(wrapperRef);

    const plotAreaWidth = width - margin.left - margin.right;
    const plotAreaHeight = height - margin.top - margin.bottom;

    const [xRange, yRange]: [number, number][] = useMemo(() => {
        if (scaleUniform) {
            return [
                plotAreaWidth > plotAreaHeight
                    ? [
                          margin.left + 0.5 * (plotAreaWidth - plotAreaHeight),
                          margin.left +
                              plotAreaHeight +
                              0.5 * (plotAreaWidth - plotAreaHeight),
                      ]
                    : [margin.left, margin.left + plotAreaWidth],
                plotAreaHeight > plotAreaWidth
                    ? [
                          margin.top +
                              plotAreaWidth +
                              0.5 * (plotAreaHeight - plotAreaWidth),
                          margin.top + 0.5 * (plotAreaHeight - plotAreaWidth),
                      ]
                    : [margin.top + plotAreaHeight, margin.top],
            ];
        } else {
            return [
                [margin.left, margin.left + plotAreaWidth],
                [margin.top + plotAreaHeight, margin.top],
            ];
        }
    }, [plotAreaWidth, plotAreaHeight, scaleUniform]);

    const context = {
        canvas,
        svgRef,
        width: width,
        height: height,
        margin,
        plotAreaWidth: width - margin.left - margin.right,
        plotAreaHeight: height - margin.top - margin.bottom,
        transformRef,
        transform,
        setTransform,
        zoom,
        xRange,
        yRange,
        xScale,
        yScale,
        setXScale,
        setYScale,
        points,
        isPointHighlighted,
        setHighlightedPoint,
        hoveredIndex,
        setHoveredIndex,
        active,
        setActive,
    };

    return (
        <Wrapper ref={wrapperRef}>
            <canvas ref={setCanvas} width={width} height={height} tw="bg-white" />
            <svg ref={svgRef} tw="absolute top-0 left-0 w-full h-full" />
            <PlotContext.Provider value={context}>{children}</PlotContext.Provider>
        </Wrapper>
    );
};

export default Plot;

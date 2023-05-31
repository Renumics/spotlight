import * as d3 from 'd3';
import {
    createContext,
    createRef,
    Dispatch,
    MutableRefObject,
    RefObject,
    SetStateAction,
} from 'react';
import { Margin, Point2d } from './types';

interface PlotContextValue {
    canvas: HTMLCanvasElement | null;
    svgRef: RefObject<SVGSVGElement>;
    width: number;
    height: number;
    margin: Margin;
    plotAreaWidth: number;
    plotAreaHeight: number;
    transformRef: MutableRefObject<d3.ZoomTransform>;
    transform: d3.ZoomTransform;
    setTransform: Dispatch<SetStateAction<d3.ZoomTransform>>;
    zoom: ReturnType<typeof d3.zoom>;
    isPointHighlighted: (index: number) => boolean;
    setHighlightedPoint: (index: number | undefined) => void;
    hoveredIndex: number | undefined;
    setHoveredIndex: (index: number | undefined) => void;
    xRange: [number, number];
    yRange: [number, number];
    xScale: d3.ScaleLinear<number, number>;
    yScale: d3.ScaleLinear<number, number>;
    setXScale: Dispatch<SetStateAction<d3.ScaleLinear<number, number>>>;
    setYScale: Dispatch<SetStateAction<d3.ScaleLinear<number, number>>>;
    points: Point2d[];
}

const defaultPlotContext: PlotContextValue = {
    canvas: null,
    svgRef: createRef(),
    width: 0,
    height: 0,
    margin: {
        left: 20,
        right: 20,
        top: 20,
        bottom: 20,
    },
    plotAreaWidth: 0,
    plotAreaHeight: 0,
    transformRef: { current: d3.zoomIdentity },
    transform: d3.zoomIdentity,
    setTransform: () => null,
    zoom: d3.zoom(),
    setHighlightedPoint: () => null,
    isPointHighlighted: () => false,
    hoveredIndex: undefined,
    setHoveredIndex: () => null,
    xRange: [0, 1],
    yRange: [0, 1],
    xScale: d3.scaleLinear(),
    yScale: d3.scaleLinear(),
    setXScale: () => null,
    setYScale: () => null,
    points: [],
};

const PlotContext = createContext(defaultPlotContext);
export default PlotContext;

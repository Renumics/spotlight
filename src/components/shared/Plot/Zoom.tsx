import * as d3 from 'd3';
import {
    forwardRef,
    ForwardRefRenderFunction,
    useContext,
    useEffect,
    useImperativeHandle,
} from 'react';
import PlotContext from './PlotContext';

export interface Handle {
    reset: () => void;
}

const Zoom: ForwardRefRenderFunction<Handle> = (_props, ref) => {
    const { svgRef, transformRef, zoom, setTransform } = useContext(PlotContext);

    useEffect(() => {
        zoom.scaleExtent([0.5, 100]).filter(
            ({ buttons, deltaX, altKey }) =>
                buttons === 4 || buttons === 3 || deltaX !== undefined || altKey
        );
    }, [zoom]);

    useImperativeHandle(
        ref,
        () => ({
            reset: () => {
                if (!svgRef.current) return;
                d3.select<Element, unknown>(svgRef.current)
                    .transition()
                    .call(zoom.transform, d3.zoomIdentity);
            },
        }),
        [zoom, svgRef]
    );

    useEffect(() => {
        if (!svgRef.current) return;

        const handleZoom = (event: d3.D3ZoomEvent<Element, unknown>) => {
            transformRef.current = event.transform;
            setTransform(event.transform);
        };
        zoom.on('zoom', handleZoom);

        d3.select<Element, unknown>(svgRef.current).call(zoom);
    }, [svgRef, zoom, setTransform, transformRef]);

    return <></>;
};

export default forwardRef<Handle>(Zoom);

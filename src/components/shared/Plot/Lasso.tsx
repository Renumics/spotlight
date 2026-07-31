import * as d3 from 'd3';
import { useContext, useEffect } from 'react';
import { theme } from 'twin.macro';
import PlotContext from './PlotContext';
import { MergeStrategy, Point2d } from './types';

interface Props {
    hidden: boolean[];
    onSelect: (key: number[], mergeStrategy: MergeStrategy) => void;
}

// Minimum distance in screen pixels between two consecutive vertices.
// Decimating the pointer trail bounds the size of the polygon without
// any visible aliasing of the outline.
const MIN_VERTEX_DISTANCE = 3;

// A polygon needs at least three vertices in order to enclose an area.
// Shorter gestures are clicks and are selected by the click handling in Points.
const MIN_VERTEX_COUNT = 3;

// The vertices are decimated in screen space already, so the default linear
// curve keeps the drawn shape identical to the tested polygon.
const buildPath = d3.line();

function findOrCreateGroup(svgElement: SVGSVGElement) {
    const svg = d3.select<SVGSVGElement, unknown>(svgElement);
    const selection = svg.select<SVGGElement>('g.lasso');
    if (!selection.empty()) {
        return selection;
    }

    const group = svg.append('g').classed('lasso', true);

    // A transparent overlay covering the whole plot provides the crosshair
    // cursor, mirroring the overlay created by d3.brush. Hovering still works
    // because pointer events bubble up to the svg root where Points listens.
    group
        .append('rect')
        .classed('overlay', true)
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('fill', 'none')
        .attr('pointer-events', 'all')
        .attr('cursor', 'crosshair');

    // The outline must never take part in hit testing, otherwise it shadows
    // the points below it and breaks hovering and clicking.
    group
        .append('path')
        .classed('outline', true)
        .attr('pointer-events', 'none')
        // d3.polygonContains uses an even odd rule, so a self intersecting
        // lasso is filled exactly like it is selected
        .attr('fill-rule', 'evenodd')
        .attr('fill', theme`colors.gray.700`)
        .attr('fill-opacity', 0.3)
        .attr('stroke', theme`colors.gray.900`)
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '4 2')
        .attr('stroke-linejoin', 'round');

    return group;
}

const Lasso = ({ hidden, onSelect }: Props): JSX.Element => {
    const { svgRef, transformRef, xScale, yScale, points } = useContext(PlotContext);

    // The group is owned by its own effect so that it is created once and keeps
    // its position in the svg. Recreating it whenever the data or the scales
    // change would move it behind the axes and thereby change which element
    // wins hit testing over the axis bands.
    useEffect(() => {
        const svgElement = svgRef.current;
        if (!svgElement) return;

        const group = findOrCreateGroup(svgElement);

        return () => {
            group.remove();
        };
    }, [svgRef]);

    useEffect(() => {
        const svgElement = svgRef.current;
        if (!svgElement) return;
        if (!transformRef.current) return;

        const group = findOrCreateGroup(svgElement);
        const outline = group.select<SVGPathElement>('path.outline');

        // The vertices are stored in untransformed plot pixels, the space
        // xScale and yScale map into. That way the lasso stays anchored to the
        // points when the plot is zoomed while the gesture is still running.
        let vertices: Point2d[] = [];
        // position of the last appended vertex in screen pixels, for decimation
        let lastPosition: Point2d | undefined;

        const clear = () => {
            vertices = [];
            lastPosition = undefined;
            outline.attr('d', '');
        };

        const render = () => {
            // always read the current transform, the mirrored react state
            // lags behind by a frame
            const transform = transformRef.current;
            const path = buildPath(vertices.map((vertex) => transform.apply(vertex)));
            outline.attr('d', path === null ? '' : `${path}Z`);
        };

        const appendVertex = (position: Point2d) => {
            if (
                lastPosition !== undefined &&
                Math.hypot(
                    position[0] - lastPosition[0],
                    position[1] - lastPosition[1]
                ) < MIN_VERTEX_DISTANCE
            ) {
                return;
            }
            lastPosition = position;
            vertices.push(transformRef.current.invert(position));
        };

        const handleDrag = (event: unknown) => {
            // d3.pointer resolves the source event of the drag event, so the
            // position is relative to the svg even outside of the plot area
            appendVertex(d3.pointer(event, svgElement));
            render();
        };

        const handleEnd = ({ sourceEvent }: { sourceEvent: MouseEvent }) => {
            const polygon = vertices;
            clear();

            // a gesture that does not enclose an area is a click and is
            // selected by Points instead
            if (polygon.length < MIN_VERTEX_COUNT) {
                return;
            }

            // reject all points outside of the bounding box of the lasso
            // before running the more expensive containment test
            let minX = Infinity;
            let minY = Infinity;
            let maxX = -Infinity;
            let maxY = -Infinity;
            for (const [x, y] of polygon) {
                minX = Math.min(minX, x);
                maxX = Math.max(maxX, x);
                minY = Math.min(minY, y);
                maxY = Math.max(maxY, y);
            }

            // project every point into the same space as the polygon and test it
            // We could use a quadtree or a similar acceleration structure to
            // speedup this process
            const selectedIndices = points
                .map((_point, i) => i)
                .filter((i) => {
                    if (hidden[i]) return false;

                    const position: Point2d = [
                        xScale(points[i][0]),
                        yScale(points[i][1]),
                    ];

                    if (
                        position[0] < minX ||
                        position[0] > maxX ||
                        position[1] < minY ||
                        position[1] > maxY
                    ) {
                        return false;
                    }

                    return d3.polygonContains(polygon, position);
                });

            const mergeMode: MergeStrategy =
                sourceEvent.ctrlKey && sourceEvent.shiftKey
                    ? 'intersect'
                    : sourceEvent.ctrlKey
                      ? 'difference'
                      : sourceEvent.shiftKey
                        ? 'union'
                        : 'replace';

            onSelect(selectedIndices, mergeMode);
        };

        const drag = d3
            .drag<SVGSVGElement, unknown>()
            // positions are computed relative to the svg itself
            .container(function () {
                return this;
            })
            // Only plain left button drags draw a lasso, alt+drag pans the plot
            // and is handled by Zoom. Note that the default filter of d3.drag
            // also rejects ctrl+drag, which we need as a merge modifier.
            .filter(({ button, altKey }) => button === 0 && !altKey)
            .on('start', (event: unknown) => {
                clear();
                handleDrag(event);
            })
            .on('drag', handleDrag)
            .on('end', handleEnd);

        // d3.drag registers namespaced listeners (mousedown.drag, ...) and
        // therefore does not replace the unnamespaced pointer event listeners
        // installed by Points on the same node.
        d3.select<SVGSVGElement, unknown>(svgElement).call(drag);

        return () => {
            // The listeners of a gesture that is still in flight live on the
            // window and cannot be removed from here, so clearing the dispatch
            // is what stops a stale onSelect from firing. Any half drawn
            // outline is dropped along with it.
            drag.on('start drag end', null);
            d3.select(svgElement).on('.drag', null);
            clear();
        };
    }, [svgRef, transformRef, xScale, yScale, points, hidden, onSelect]);

    return <></>;
};

export default Lasso;

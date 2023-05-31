import * as d3 from 'd3';
import { useContext, useEffect } from 'react';
import PlotContext from './PlotContext';
import { MergeStrategy, Point2d } from './types';

interface Props {
    hidden: boolean[];
    onSelect: (key: number[], mergeStrategy: MergeStrategy) => void;
}

function findOrCreateGroup(svgElement: SVGSVGElement) {
    const svg = d3.select<SVGSVGElement, unknown>(svgElement);
    const selection = svg.select<SVGGElement>('g.brush');
    if (selection.empty()) {
        return svg.append('g').classed('brush', true);
    }
    return selection;
}

const Brush = ({ hidden, onSelect }: Props): JSX.Element => {
    const { svgRef, transformRef, xScale, yScale, points } = useContext(PlotContext);

    useEffect(() => {
        const svgElement = svgRef.current;
        if (!svgElement) return;
        if (!transformRef.current) return;

        const brush = d3
            .brush()
            .filter(({ button, altKey }) => button === 0 && !altKey)
            .keyModifiers(false);

        const brushGroup = findOrCreateGroup(svgElement);

        const handleBrush = ({
            selection,
            sourceEvent,
        }: {
            selection: d3.BrushSelection;
            sourceEvent: MouseEvent;
        }) => {
            if (selection === null) {
                return;
            }

            // first project the selection area into the data domain
            // note: we explicitly cast selection start and end because it is always a 2d region
            const canvasStart = transformRef.current.invert(selection[0] as Point2d);
            const canvasEnd = transformRef.current.invert(selection[1] as Point2d);

            const dataStart = [
                xScale.invert(canvasStart[0]),
                yScale.invert(canvasEnd[1]),
            ];
            const dataEnd = [
                xScale.invert(canvasEnd[0]),
                yScale.invert(canvasStart[1]),
            ];

            // simply filter all points that are inside the selection
            // We could use a quadtree or a similar acceleration structure to speedup this process
            const selectedIndices = points
                .map((_point, i) => i)
                .filter((i) => {
                    const [x, y] = points[i];
                    return (
                        !hidden[i] &&
                        x >= dataStart[0] &&
                        x <= dataEnd[0] &&
                        y >= dataStart[1] &&
                        y <= dataEnd[1]
                    );
                });

            const mergeMode: MergeStrategy =
                sourceEvent.ctrlKey && sourceEvent.shiftKey
                    ? 'intersect'
                    : sourceEvent.ctrlKey
                    ? 'difference'
                    : sourceEvent.shiftKey
                    ? 'union'
                    : 'replace';

            brushGroup.call(brush.move, null);
            onSelect(selectedIndices, mergeMode);
        };

        brush.on('end', handleBrush);
        brushGroup.call(brush);
    }, [svgRef, transformRef, xScale, yScale, points, hidden, onSelect]);

    return <></>;
};

export default Brush;

import UITooltip from '../../ui/Tooltip';
import { useContext, useEffect, useMemo, useState } from 'react';
import PlotContext from './PlotContext';

interface Props {
    content: (index?: number) => JSX.Element | undefined;
}

const Tooltip = ({ content }: Props): JSX.Element => {
    const { hoveredIndex, canvas, svgRef } = useContext(PlotContext);

    const [tooltipIndex, setTooltipIndex] = useState(hoveredIndex);
    const [tooltipVisible, setTooltipVisible] = useState(false);

    const tooltipContent = useMemo(() => {
        if (tooltipIndex === undefined) return undefined;
        return content(tooltipIndex);
    }, [content, tooltipIndex]);

    useEffect(() => {
        if (!canvas) return;

        if (hoveredIndex !== undefined) {
            setTooltipIndex(hoveredIndex);
            setTooltipVisible(true);
        } else {
            setTooltipVisible(false);
        }
    }, [canvas, hoveredIndex]);

    return (
        <UITooltip
            content={tooltipContent}
            disabled={false}
            visible={tooltipVisible}
            followCursor={true}
            borderless={true}
            reference={svgRef}
        />
    );
};

export default Tooltip;

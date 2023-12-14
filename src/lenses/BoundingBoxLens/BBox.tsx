import chroma from 'chroma-js';
import { theme } from 'twin.macro';

interface BBoxProps {
    x: number;
    y: number;
    width: number;
    height: number;
    color: string;
    label: string;
}

const WHITE = chroma(theme`colors.white`);
const BLACK = chroma(theme`colors.black`);

const BBox = ({ x, y, width, height, color, label }: BBoxProps) => {
    const textColor =
        chroma.contrast(color, WHITE) > chroma.contrast(color, BLACK) ? WHITE : BLACK;

    return (
        <g>
            <rect
                x={x}
                y={y}
                width={width}
                height={height}
                fill="none"
                stroke={color}
                strokeWidth={2}
            ></rect>
            <rect
                x={x}
                y={y - 11}
                width={width}
                height={12}
                fill={color}
                stroke={color}
                strokeWidth={2}
            ></rect>
            <text x={x} y={y} fontSize={12} stroke={textColor.hex()}>
                {label}
            </text>
        </g>
    );
};

export default BBox;

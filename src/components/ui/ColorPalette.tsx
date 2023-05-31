import _ from 'lodash';
import { FunctionComponent, useEffect, useRef } from 'react';
import { Palette } from '../../palettes';

interface Props {
    palette: Palette;
    width?: number;
    height?: number;
}

const ColorPalette: FunctionComponent<Props> = ({
    palette,
    width = 150,
    height = 8,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) {
            return;
        }
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            return;
        }

        if (palette.kind === 'constant') {
            ctx.fillStyle = palette.scale()(0).hex();
            ctx.fillRect(0, 0, width, height);
        }
        if (palette.kind === 'continuous') {
            const gradient = ctx.createLinearGradient(0, 0, width, 0);
            const valSteps = _.range(0, 1, 1 / 50);
            valSteps.forEach((val) => {
                gradient.addColorStop(val, palette.scale()(val).hex());
            });
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, width, height);
        }
        if (palette.kind === 'categorical') {
            const classCount = palette.maxClasses;
            const valSteps = _.range(0, classCount);
            const categoryWidth = width / classCount;
            valSteps.forEach((val, i) => {
                ctx.fillStyle = palette.scale()(val).hex();
                ctx.fillRect(i * categoryWidth, 0, categoryWidth, height);
            });
        }
    }, [canvasRef, palette, height, width]);

    return <canvas ref={canvasRef} width={width} height={height} />;
};

export default ColorPalette;

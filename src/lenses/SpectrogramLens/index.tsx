import useResizeObserver from '@react-hook/resize-observer';
import LoadingIndicator from '../../components/LoadingIndicator';
import * as d3 from 'd3';
import { isAudio } from '../../datatypes';
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import tw, { styled, theme } from 'twin.macro';
import { default as WaveSurfer, default as WebAudio } from 'wavesurfer.js';
import { ColorsState, useColors } from '../../stores/colors';
import { Lens } from '../../types';
import useSetting from '../useSetting';
import MenuBar from './MenuBar';
import { fixWindow, freqType, unitType } from './Spectrogram';

const Container = tw.div`flex flex-col w-full h-full items-stretch justify-center`;
const EmptyNote = styled.p`
    color: ${theme`colors.gray.500`};
    ${tw`flex h-full items-center justify-center`}
`;

interface WebAudio_ extends WebAudio {
    buffer: AudioBuffer;
}

const LOG_DOMAIN_LOWER_LIMIT = 10;
const FFT_SAMPLES = 1024;

/*
 * Redraws the scale for resized spectrogram
 */
const drawScale = (
    scaleContainer: SVGSVGElement | null,
    sampleRate: number,
    isLogarithmic: boolean
) => {
    const height = scaleContainer?.clientHeight ?? FFT_SAMPLES / 2;
    const upperLimit = sampleRate / 2;
    const numTicks = Math.round(height / (isLogarithmic ? 20 : 30));

    let axis;

    if (isLogarithmic) {
        const domain = [LOG_DOMAIN_LOWER_LIMIT, upperLimit];
        const range = [height, 0];
        const scale = d3.scaleLog(domain, range);

        axis = d3
            .axisRight(scale)
            .scale(scale)
            .tickPadding(1)
            .tickSizeOuter(0)
            .ticks(numTicks, (x: number) => {
                return `${freqType(x).toFixed(1)} ${unitType(x)}`;
            });
    } else {
        const domain = [upperLimit, 0];
        const range = [0, height];
        const scale = d3.scaleLinear(domain, range);

        axis = d3
            .axisRight(scale)
            .scale(scale)
            .tickPadding(1)
            .tickSizeOuter(0)
            .tickArguments([numTicks])
            .tickFormat((x) => {
                return `${freqType(x.valueOf()).toFixed(1)} ${unitType(x.valueOf())}`;
            });
    }

    d3.select(scaleContainer)
        .select<SVGSVGElement>('g')
        .call(axis)
        .attr('color', theme`colors.white`);

    // Offset ticks upwards
    d3.select(scaleContainer)
        .select<SVGSVGElement>('g')
        .selectAll('text')
        .attr('transform', 'translate(-1,-5)')
        .attr('color', theme`colors.white`);
};

const SpectrogramLens: Lens = ({ columns, urls, values }) => {
    const windowIndex = columns.findIndex((col) => col.type.kind === 'Window');
    const audioIndex = columns.findIndex((col) => col.type.kind === 'Audio');
    const window = values[windowIndex] as [number, number] | undefined;
    const url = urls[audioIndex];

    const [isComputing, setIsComputing] = useState(true);
    const [isValidWindow, setIsValidWindow] = useState(true);

    const colorPaletteSelector = (c: ColorsState) => c.continuousPalette;

    const waveform = useRef<WaveSurfer>();

    const spectrogramCanvas = useRef<HTMLCanvasElement>(null);

    const wavesurferElement = useRef<HTMLDivElement>(null);
    const wavesurferContainer = useRef<HTMLDivElement>(null);
    const scaleContainer = useRef<SVGSVGElement>(null);
    const mouseLabel = useRef<SVGTextElement>(null);

    const [isLogScale, setIsLogScale] = useSetting('isLogScale', true);
    const [size, setSize] = useState([0, 0]);

    const colorPalette = useColors(colorPaletteSelector);

    // Waveform height does not automatically adapt to container size
    useResizeObserver(wavesurferContainer.current, () => {
        if (url === undefined) return;

        const backend = waveform.current?.backend as unknown as WebAudio_;

        const width = wavesurferContainer.current?.clientWidth ?? 1;
        const height = wavesurferContainer.current?.clientHeight ?? 1;

        setSize([width, height]);

        // Trigger redraw
        drawScale(scaleContainer.current, backend.buffer?.sampleRate ?? 0, isLogScale);
    });

    useEffect(() => {
        if (size[0] === 0) return;

        if (spectrogramCanvas.current) {
            spectrogramCanvas.current.width = size[0];
            spectrogramCanvas.current.height = size[1];
        }

        const worker = new Worker(new URL('SpectrogramWorker.js', import.meta.url));

        worker.onmessage = (e) => {
            if (!waveform.current) return;
            if (!spectrogramCanvas.current) return;

            setIsComputing(false);

            // Get the canvas render context 2D
            const spectrCc = spectrogramCanvas.current.getContext('2d');

            const backend = waveform.current.backend as unknown as WebAudio_;

            const frequenciesData = e.data;

            const upperLimit = backend.buffer?.sampleRate / 2;

            // 10, ..., half-samplerate (default 22050)
            const domain = [LOG_DOMAIN_LOWER_LIMIT, upperLimit];

            const width = spectrogramCanvas.current.width;
            const height = spectrogramCanvas.current.height;

            // 0, ..., canvas-height
            const range = [0, height];

            if (!spectrCc) {
                return;
            }

            const imageData = new ImageData(width, height);

            const scale = d3.scaleLog(domain, range);

            const heightScale = isLogScale
                ? d3.scaleLinear(domain, [0, FFT_SAMPLES / 2 - 1])
                : d3.scaleLinear(domain, [0, upperLimit]);

            const widthScale = d3.scaleLinear([0, width], [0, frequenciesData.length]);
            const colorMap = colorPalette.scale().colors(256, 'gl');

            for (let y = 0; y < height; y++) {
                const value = isLogScale
                    ? heightScale(scale.invert(height - y))
                    : Math.abs(heightScale(height - y));
                const indexA = Math.floor(value);
                const indexB = indexA + 1;
                const alpha = value - indexA;

                for (let x = 0; x < width; x++) {
                    const x_index = Math.floor(widthScale(x));

                    const value_a = frequenciesData[x_index][indexA];
                    const value_b = frequenciesData[x_index][indexB];

                    const color_a = colorMap[value_a];
                    const color_b = colorMap[value_b];

                    const offset = (y * width + x) * 4;

                    // Linear interpolation between two samples
                    imageData.data[offset + 0] =
                        255 * (color_b[0] * alpha + color_a[0] * (1 - alpha));
                    imageData.data[offset + 1] =
                        255 * (color_b[1] * alpha + color_a[1] * (1 - alpha));
                    imageData.data[offset + 2] =
                        255 * (color_b[2] * alpha + color_a[2] * (1 - alpha));

                    imageData.data[offset + 3] = 255;
                }
            }

            spectrCc.putImageData(imageData, 0, 0);
        };

        const drawSpectrogram = () => {
            if (!waveform.current) return;
            if (!spectrogramCanvas.current) return;

            const width = spectrogramCanvas.current.clientWidth;
            const duration = waveform.current.getDuration() ?? 1;

            const fixedWindow: [number, number] = fixWindow(window, duration);

            const backend = waveform.current.backend as unknown as WebAudio_;

            const start = (fixedWindow[0] / duration) * backend.buffer.length;
            const end = (fixedWindow[1] / duration) * backend.buffer.length;

            if (start + FFT_SAMPLES > end) {
                setIsValidWindow(false);
                return;
            }

            worker?.postMessage({
                channelData: backend.buffer.getChannelData(0).slice(start, end),
                sampleRate: backend.buffer.sampleRate,
                width: width,
                fftSamples: FFT_SAMPLES,
                windowFunc: undefined,
                alpha: undefined,
            });

            setIsValidWindow(true);
            setIsComputing(true);
        };

        if (waveform.current?.isReady) {
            drawSpectrogram();
        } else {
            waveform?.current?.on('ready', drawSpectrogram);
        }

        return () => {
            worker.terminate();
        };
    }, [window, isLogScale, colorPalette, size]);

    const handleToggleLogScale = useCallback(
        (logScaled: boolean) => {
            setIsLogScale(logScaled);

            const backend = waveform.current?.backend as unknown as WebAudio_;

            drawScale(
                scaleContainer.current,
                backend.buffer?.sampleRate ?? 0,
                logScaled
            );
        },
        [setIsLogScale]
    );

    useEffect(() => {
        waveform?.current?.on('ready', () => {
            const backend = waveform.current?.backend as unknown as WebAudio_;

            // Draw initial scale
            drawScale(
                scaleContainer.current,
                backend.buffer?.sampleRate ?? 0,
                isLogScale
            );
        });
    }, [isLogScale]);

    useLayoutEffect(() => {
        // No setup needed, since no audio track
        if (url === undefined) return;

        const container = wavesurferContainer.current;
        if (!container || !wavesurferElement.current) return;

        // Initialize wavesurfer
        waveform.current = WaveSurfer.create({
            height: 0,
            container: wavesurferElement.current,
            backend: 'WebAudio',
        });
        waveform.current?.load(url);

        d3.select(container)
            .on('mousemove', (e) => {
                const backend = waveform.current?.backend as unknown as WebAudio_;
                const height = scaleContainer.current?.clientHeight ?? 512;
                const upperLimit = backend.buffer?.sampleRate / 2;
                const coords = d3.pointer(e);

                if (isLogScale) {
                    const domain = [LOG_DOMAIN_LOWER_LIMIT, upperLimit];
                    const range = [0, height];

                    const scale = d3.scaleLog(domain, range);
                    const value = scale.invert(height - coords[1]);
                    d3.select(mouseLabel.current)
                        .text(`${freqType(value).toFixed(1)} ${unitType(value)}`)
                        .attr('x', coords[0])
                        .attr('y', coords[1])
                        .attr('font-size', 10)
                        .attr('fill', theme`colors.white`);
                } else {
                    const domain = [upperLimit, 0];
                    const range = [0, height];
                    const scale = d3.scaleLinear(domain, range);
                    const value = scale.invert(coords[1]);
                    d3.select(mouseLabel.current)
                        .text(`${freqType(value).toFixed(1)} ${unitType(value)}`)
                        .attr('x', coords[0])
                        .attr('y', coords[1])
                        .attr('font-size', 10)
                        .attr('fill', theme`colors.white`);
                }
            })
            .on('mouseenter', () => {
                d3.select(mouseLabel.current).style('opacity', 1);
            })
            .on('mouseleave', () => {
                d3.select(mouseLabel.current).style('opacity', 0);
            });

        return () => {
            waveform?.current?.destroy();
            d3.select(container)
                .on('mousemove', null)
                .on('mouseenter', null)
                .on('mouseleave', null);
        };
    }, [url, isLogScale, colorPalette]);

    return (
        <Container>
            {isComputing && (
                <div tw="absolute h-full w-full">
                    <LoadingIndicator />
                </div>
            )}
            {!isValidWindow && (
                <EmptyNote tw="absolute h-full w-full">Window too short!</EmptyNote>
            )}
            <div ref={wavesurferContainer} tw="flex-grow overflow-auto relative">
                <svg ref={scaleContainer} tw="h-full w-full absolute z-10">
                    <text ref={mouseLabel} />
                    <g />
                </svg>
                {!isComputing &&
                    (url ? (
                        ''
                    ) : (
                        <EmptyNote tw="absolute h-full w-full">No Data</EmptyNote>
                    ))}
                <canvas
                    id="spectrogram-canvas"
                    ref={spectrogramCanvas}
                    tw="h-full w-full"
                ></canvas>

                <div ref={wavesurferElement} />
            </div>
            {
                // Add the menubar as last component, so that it is rendered on top
                // We don't use a z-index for this, because it interferes with the rendering of the contained menus
            }

            <MenuBar
                tw="z-10"
                isLogScale={isLogScale}
                onToggleScale={handleToggleLogScale}
            />
        </Container>
    );
};

SpectrogramLens.key = 'SpectrogramView';
SpectrogramLens.defaultHeight = 120;
SpectrogramLens.displayName = 'Spectrogram';
SpectrogramLens.dataTypes = ['Audio', 'Window'];
SpectrogramLens.multi = true;
SpectrogramLens.filterAllowedColumns = (allColumns, selectedColumns) => {
    if (selectedColumns.length === 2) return [];
    switch (selectedColumns[0]?.type.kind) {
        case 'Audio':
            return allColumns.filter((col) => col.type.kind === 'Window');
        case 'Window':
            return allColumns.filter((col) => col.type.kind === 'Audio');
    }
    return allColumns.filter((col) => ['Audio', 'Window'].includes(col.type.kind));
};
SpectrogramLens.isSatisfied = (columns) => {
    return columns.some((col) => isAudio(col.type));
};

export default SpectrogramLens;

import * as Comlink from 'comlink';
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
import { fixWindow, freqType, unitType, amplitudeToDb, hzToMel } from './Spectrogram';

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
    scale: string
) => {
    const height = scaleContainer?.clientHeight ?? FFT_SAMPLES / 2;
    const upperLimit = sampleRate / 2;
    let numTicks = 0;

    if (scale === 'logarithmic') {
        numTicks = Math.round(height / 20);
    } else if (scale === 'linear') {
        numTicks = Math.round(height / 30);
    } else {
        numTicks = 5;
    }

    let axis;

    if (scale === 'logarithmic') {
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

    const [freqScale, setFreqScale] = useSetting('freqScale', 'linear');
    const [ampScale, setAmpScale] = useSetting('ampScale', 'decibel');
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
        drawScale(scaleContainer.current, backend.buffer?.sampleRate ?? 0, freqScale);
    });

    useEffect(() => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const worker: any = Comlink.wrap(
            new Worker(new URL('./SpectrogramWorker.ts', import.meta.url), {
                type: 'module',
            })
        );

        const drawSpectrogram = async () => {
            if (!waveform.current) return;
            if (!spectrogramCanvas.current) return;

            if (size[0] === 0) return;

            if (spectrogramCanvas.current) {
                spectrogramCanvas.current.width = size[0];
                spectrogramCanvas.current.height = size[1];
            }

            const backend = waveform.current.backend as unknown as WebAudio_;
            const buffer = backend.buffer;
            if (!buffer) return;

            const width = spectrogramCanvas.current.clientWidth;
            const height = spectrogramCanvas.current.height;
            const duration = waveform.current.getDuration() ?? 1;

            const fixedWindow: [number, number] = fixWindow(window, duration);

            const start = (fixedWindow[0] / duration) * buffer.length;
            const end = (fixedWindow[1] / duration) * buffer.length;

            if (start + FFT_SAMPLES > end) {
                setIsValidWindow(false);
                return;
            }

            //console.log(JSON.stringify((buffer.getChannelData(0).slice(start, end)))
            //const slice = buffer.getChannelData(0).slice(start, end);
            const arr = buffer.getChannelData(0).slice(start, end);
            console.log(Math.max(...arr), Math.min(...arr));
            const frequenciesData = await worker(
                FFT_SAMPLES,
                backend.windowFunc,
                backend.alpha,
                width,
                FFT_SAMPLES,
                arr
            );

            console.log(frequenciesData);
            console.log(frequenciesData.length);
            console.log(frequenciesData[0].length);

            setIsComputing(false);

            // Get the canvas render context 2D
            const spectrCc = spectrogramCanvas.current.getContext('2d');

            if (!spectrCc) {
                return;
            }

            const upperLimit = backend.buffer?.sampleRate / 2;

            // 10, ..., half-samplerate (default 22050)
            const domain = [LOG_DOMAIN_LOWER_LIMIT, upperLimit];

            // 0, ..., canvas-height
            const range = [0, height];

            const imageData = new ImageData(width, height);

            const scaleFunc = d3.scaleLog(domain, range);

            // Default to linear scale
            let heightScale = d3.scaleLinear(domain, [0, upperLimit]);

            if (freqScale === 'logarithmic') {
                heightScale = d3.scaleLinear(domain, [0, FFT_SAMPLES / 2 - 1]);
            } else if (freqScale === 'linear') {
                heightScale = d3.scaleLinear(domain, [0, upperLimit]);
            }

            const widthScale = d3.scaleLinear([0, width], [0, frequenciesData.length]);

            let drawData = [];
            //let colorScale: chroma.Scale<chroma.Color>;

            let min = 0;
            let max = 0;

            if (ampScale === 'decibel') {
                let ref = 0;
                for (let i = 0; i < frequenciesData.length; i++) {
                    const maxI = Math.max(...frequenciesData[i]);

                    if (maxI > ref) {
                        ref = maxI;
                    }
                }
                //const top_db = 80;
                const amin = 1e-5;

                // Convert amplitudes to decibels
                for (let i = 0; i < frequenciesData.length; i++) {
                    const col = [];

                    for (let j = 0; j < frequenciesData[i].length; j++) {
                        const amplitude = frequenciesData[i][j];
                        col[j] = amplitudeToDb(amplitude, ref, amin);

                        if (col[j] > max) {
                            max = col[j];
                        }

                        if (col[j] < min) {
                            min = col[j];
                        }
                    }

                    drawData[i] = col;
                }
            } else if (ampScale === 'mel') {
                for (let i = 0; i < frequenciesData.length; i++) {
                    const col = [];

                    for (let j = 0; j < frequenciesData[i].length; j++) {
                        const amplitude = frequenciesData[i][j];
                        col[j] = hzToMel(amplitude ** 2);

                        if (col[j] > max) {
                            max = col[j];
                        }

                        if (col[j] < min) {
                            min = col[j];
                        }
                    }
                    drawData[i] = col;
                }
            } else {
                // ampScale === 'linear'
                for (let i = 0; i < frequenciesData.length; i++) {
                    const maxI = Math.max(...frequenciesData[i]);
                    const minI = Math.min(...frequenciesData[i]);

                    if (maxI > max) {
                        max = maxI;
                    }
                    if (minI < min) {
                        min = minI;
                    }
                }
                drawData = frequenciesData;
            }
            const colorScale = colorPalette.scale().domain([min, max]);

            for (let y = 0; y < height; y++) {
                let value = 0;

                if (freqScale === 'logarithmic') {
                    value = heightScale(scaleFunc.invert(height - y));
                } else if (freqScale === 'linear') {
                    value = Math.abs(heightScale(height - y));
                }

                const indexA = Math.floor(value);
                const indexB = indexA + 1;
                const alpha = value - indexA;

                for (let x = 0; x < width; x++) {
                    const x_index = Math.floor(widthScale(x));

                    const value_a = drawData[x_index][indexA];
                    const value_b = drawData[x_index][indexB];

                    // eslint-disable-next-line
                    // @ts-ignore
                    const color_a = colorScale(value_a).rgb();
                    // eslint-disable-next-line
                    // @ts-ignore
                    const color_b = colorScale(value_b).rgb();

                    const offset = (y * width + x) * 4;

                    // Linear interpolation between two samples
                    imageData.data[offset + 0] =
                        color_b[0] * alpha + color_a[0] * (1 - alpha);
                    imageData.data[offset + 1] =
                        color_b[1] * alpha + color_a[1] * (1 - alpha);
                    imageData.data[offset + 2] =
                        color_b[2] * alpha + color_a[2] * (1 - alpha);

                    imageData.data[offset + 3] = 255;
                }
            }

            spectrCc.putImageData(imageData, 0, 0);

            setIsValidWindow(true);
        };

        if (waveform.current?.isReady) {
            drawSpectrogram();
        } else {
            waveform?.current?.on('ready', drawSpectrogram);
        }

        return () => {
            worker.terminate();
        };
    }, [window, freqScale, ampScale, colorPalette, size]);

    const handleFreqScaleChange = useCallback(
        (scale: string) => {
            setFreqScale(scale);

            const backend = waveform.current?.backend as unknown as WebAudio_;

            drawScale(scaleContainer.current, backend.buffer?.sampleRate ?? 0, scale);
        },
        [setFreqScale]
    );

    const handleAmpScaleChange = useCallback(
        (scale: string) => {
            setAmpScale(scale);
        },
        [setAmpScale]
    );

    useEffect(() => {
        waveform?.current?.on('ready', () => {
            const backend = waveform.current?.backend as unknown as WebAudio_;

            // Draw initial scale
            drawScale(
                scaleContainer.current,
                backend.buffer?.sampleRate ?? 0,
                freqScale
            );
        });
    }, [freqScale]);

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

                if (freqScale === 'logarithmic') {
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
                    //if (freqScale === 'linear') {
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
    }, [url, freqScale, colorPalette]);

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
                availableFreqScales={['linear', 'logarithmic']}
                freqScale={freqScale}
                onChangeFreqScale={handleFreqScaleChange}
                availableAmpScales={['decibel', 'linear', 'mel']}
                ampScale={ampScale}
                onChangeAmpScale={handleAmpScaleChange}
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

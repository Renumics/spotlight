import useResizeObserver from '@react-hook/resize-observer';
import MaximizeIcon from '../../../icons/Maximize';
import ResetIcon from '../../../icons/Reset';
import RepeatIcon from '../../../icons/Repeat';
import Button from '../../ui/Button';
import * as d3 from 'd3';
import { useEffect, useLayoutEffect, useRef, useState, WheelEvent } from 'react';
import {
    BsPauseCircle,
    BsPlayCircle,
    BsPlayCircleFill,
    BsStopCircle,
} from 'react-icons/bs';
import tw, { styled, theme } from 'twin.macro';
import { notifyProblem } from '../../../notify';
import WaveSurfer from 'wavesurfer.js';
import RegionsPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.regions.min.js';
import CursorPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.cursor.min.js';

// Maximum zoom level for waveform
const MAX_ZOOM = 2500;

const Container = tw.div`flex flex-col w-full h-full items-stretch justify-center`;

const Toolbar = tw.div`flex flex-row items-center justify-center p-px`;
const ToolbarButton = tw(Button)`rounded-none py-0`;

const EmptyNote = styled.p`
    color: ${theme`colors.gray.500`};
    ${tw`flex h-full items-center justify-center`}
`;

const WaveStyles = styled.div`
    region.wavesurfer-region {
        ${tw`z-40! opacity-30! border-blue-500 hover:opacity-50!`};
        border-left-width: 2px;
        border-right-width: 2px;
    }
    handle.wavesurfer-handle {
        ${tw`bg-black! w-0!`}
    }

    handle.wavesurfer-handle::before {
        content: '';
        display: block;
        width: 10px;
        height: 100%;
        margin-left: -5px;
    }
`;

// Only one active widget at a time
let ActiveWidget: WaveSurfer | null;

/*
 * Draws a new timeline
 */
const redrawTimeline = (
    timelineContainer: SVGSVGElement | null,
    waveform: WaveSurfer | undefined
) => {
    const width = timelineContainer?.clientWidth ?? 10;
    const duration = waveform?.getDuration() ?? 0;

    // Don't draw timeline for empty files
    if (duration === 0) return;

    // How many ticks can we fit in the container
    const numTicks = Math.floor(width / 60);

    // Date constructor expects milliseconds
    const durationMillis = 1000 * duration;
    const durationDate = new Date(durationMillis);

    // Check in what order of magnitude we are
    // in order to omit too many leading zeros
    const hasHours = !!durationDate.getUTCHours();
    const hasMinutes = !!durationDate.getMinutes();
    const hasSeconds = !!durationDate.getSeconds();

    const drawerWidth = waveform?.drawer.getWidth();
    const offsetLeft = waveform?.drawer.getScrollX();
    const offsetRight = offsetLeft + drawerWidth;
    const secPerPx = duration / (waveform?.drawer.wrapper.scrollWidth ?? 0);

    const lowerTime = offsetLeft * secPerPx;
    const upperTime = offsetRight * secPerPx;

    const domain = [lowerTime, upperTime];
    const range = [0, width];
    const timeline = d3.scaleLinear(domain, range);

    const axis = d3
        .axisBottom(timeline)
        .scale(timeline)
        .tickPadding(1)
        .tickSizeOuter(0)
        .tickArguments([numTicks])
        .tickFormat((x) => {
            const val = Number(x.valueOf());

            if (val === 0) {
                return '0ms';
            }

            // Seconds to milliseconds
            const date = new Date(val * 1000);

            let formatString = '%Lms';

            // Only add minutes if necessary
            if (hasHours) {
                formatString = '%H:%Mh';
            } else if (hasMinutes) {
                formatString = '%M:%Sm';
            } else if (hasSeconds) {
                formatString = '%S:%Ls';
            }

            return d3.utcFormat(formatString)(date);
        });

    d3.select(timelineContainer)
        .select<SVGSVGElement>('g')
        .call(axis)
        .attr('color', theme`colors.gray.800`);

    d3.select(timelineContainer)
        .select<SVGSVGElement>('g')
        .selectAll('.tick')
        .select('text')
        .attr('text-anchor', 'start');

    // Fit line to container width
    d3.select(timelineContainer)
        .select('.domain')
        .attr('d', 'M0,0H' + width);
};

interface Props {
    url?: string;
    peaks?: number[];
    windows: [number, number][];
    editable: boolean;
    optional: boolean;
    showControls?: boolean;
    repeat?: boolean;
    onChangeRepeat?: (enabled: boolean) => void;
    onEditWindow?: (window: [number, number]) => void;
    onDeleteWindow?: () => void;
    onRegionEnter?: (windowIndex: number) => void;
    onRegionLeave?: (windowIndex: number) => void;
    onRegionClick?: (windowIndex: number) => void;
}

const AudioViewer = ({
    url,
    peaks,
    windows,
    editable,
    optional,
    showControls,
    repeat,
    onChangeRepeat,
    onEditWindow,
    onDeleteWindow,
    onRegionEnter,
    onRegionLeave,
    onRegionClick,
}: Props) => {
    const audioRef = useRef<HTMLAudioElement>(null);
    const waveform = useRef<WaveSurfer>();
    const region = useRef<WaveSurfer>();
    const wavesurferElement = useRef<HTMLDivElement>(null);
    const wavesurferContainer = useRef<HTMLDivElement>(null);
    const timelineContainer = useRef<SVGSVGElement>(null);

    const [isPlaying, setIsPlaying] = useState(false);
    const [isReady, setIsReady] = useState(false);

    const [_repeat, _setRepeat] = useState(false);
    repeat = repeat ?? _repeat;
    onChangeRepeat = onChangeRepeat ?? _setRepeat;
    const toggleRepeat = () => onChangeRepeat?.(!repeat);

    const redrawWaveform = (height: number) => {
        waveform.current?.setHeight(height);
    };

    // Waveform height does not automatically adapt to container size
    useResizeObserver(wavesurferContainer.current, (entries) => {
        const height = entries.contentRect['height'];

        // Trigger redraw
        redrawWaveform(height);
        redrawTimeline(timelineContainer.current, waveform.current);
    });

    useLayoutEffect(() => {
        // No setup needed, since no audio track
        if (url === undefined) return;
        if (wavesurferElement.current == null) return;

        setIsReady(false);

        // Initialize waveform and plugin
        waveform.current = WaveSurfer.create({
            cursorWidth: 1,
            height: 0,
            container: wavesurferElement.current,
            backend: 'MediaElement',
            mediaControls: false,
            fillParent: true,
            scrollParent: false,
            progressColor: theme`colors.blue.600`,
            responsive: false,
            waveColor: theme`colors.gray.500`,
            cursorColor: 'transparent',
            hideScrollbar: false,
            autoCenter: false,
            barRadius: 1,
            barHeight: 2,
            plugins: [
                CursorPlugin.create({
                    showTime: true,
                    customShowTimeStyle: {
                        'font-size': theme`fontSize.xs`,
                        'margin-left': '4px',
                    },
                    opacity: 0.5,
                    followCursorY: true,
                }),
                RegionsPlugin.create({
                    dragSelection: editable,
                    maxRegions: editable ? 1 : 100,
                }),
            ],
        });

        waveform.current.on('region-click', (_region, event) => {
            event.stopPropagation();

            onRegionClick?.(parseInt(_region.id));
        });

        waveform.current.on('region-mouseenter', (_region, event) => {
            event.stopPropagation();

            onRegionEnter?.(parseInt(_region.id));
        });

        waveform.current.on('region-mouseleave', (_region, event) => {
            event.stopPropagation();

            onRegionLeave?.(parseInt(_region.id));
        });

        waveform.current.on('region-dblclick', (_region, event) => {
            if (!editable) return;
            if (!optional) {
                notifyProblem(
                    {
                        type: 'ColumnNotOptional',
                        title: 'Cannot delete window',
                        detail: `Window column is not optional`,
                    },
                    'warning'
                );
                return;
            }
            onDeleteWindow?.();

            waveform.current?.regions.clear();
            region.current = undefined;

            event.stopPropagation();
        });

        waveform.current.on('region-created', (_region) => {
            region.current = _region;
        });

        waveform.current.on('region-update-end', (region) => {
            onEditWindow?.([region.start, region.end]);

            // Wavesurfer prevents passing click events to ui
            // so we need to click manually once
            document.body.click();
        });

        waveform.current.on('scroll', () => {
            redrawTimeline(timelineContainer.current, waveform.current);
        });

        // Draw the timeline when the track has finished loading
        waveform.current.on('ready', () => {
            redrawTimeline(timelineContainer.current, waveform.current);

            const height = wavesurferContainer.current?.clientHeight ?? 80;
            redrawWaveform(height);

            setIsReady(true);

            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            //(waveform.current?.backend as any).media.loop = repeat;
        });

        // In case this widget was paused from the outside
        waveform.current.on('pause', () => {
            setIsPlaying(false);
        });

        // Reset cursor, clear playing state
        waveform.current?.on('finish', () => {
            setIsPlaying(false);
            waveform.current?.stop();
            ActiveWidget = null;
        });

        return () => {
            region.current = undefined;
            waveform.current?.destroy();
            waveform.current = undefined;
        };
    }, [
        url,
        editable,
        optional,
        onDeleteWindow,
        onEditWindow,
        onRegionClick,
        onRegionEnter,
        onRegionLeave,
    ]);

    useEffect(() => {
        (waveform.current?.backend as any).media.loop = repeat;
    }, [repeat]);

    useEffect(() => {
        if (!waveform.current?.isReady) return;

        waveform.current.regions.clear();

        for (const [id, window] of windows.entries()) {
            if (!window) continue;

            const start = isNaN(window[0]) ? 0 : window[0];
            const end = isNaN(window[1])
                ? waveform.current?.getDuration() ?? 0
                : window[1];

            waveform.current.regions.add({
                start: Math.min(start, end),
                end: Math.max(start, end),
                id: id.toString(),
                drag: editable,
                resize: editable,
                color: start > end ? theme`colors.red.500` : theme`colors.blue.500`,
            });
        }
    }, [isReady, windows, editable]);

    useEffect(() => {
        if (!audioRef.current) return;
        if (url && peaks) {
            waveform.current?.load(audioRef.current, peaks);
        } else {
            redrawTimeline(timelineContainer.current, waveform.current);
        }
    }, [url, peaks]);

    const switchActiveWidget = () => {
        if (!waveform.current?.isReady) return;

        if (ActiveWidget !== waveform.current) {
            // Another widget is playing but play was pressed here
            // therefore pause active widget and overwrite with this

            // Pause currently active widget
            if (ActiveWidget?.isReady) ActiveWidget.pause();

            // Set this widget active
            ActiveWidget = waveform.current;
        }
    };
    /*
     * Player controls
     */
    const playRegion = () => {
        if (!waveform.current?.isReady) return;

        switchActiveWidget();

        if (region.current) {
            region.current.play();
            setIsPlaying(waveform.current.isPlaying());
        }
    };

    const playPause = () => {
        if (!waveform.current?.isReady) return;

        switchActiveWidget();

        waveform.current.playPause();

        setIsPlaying(waveform.current.isPlaying());
    };

    const stopPlaying = () => {
        if (waveform.current?.isReady) {
            waveform.current?.stop();
            setIsPlaying(false);

            if (ActiveWidget === waveform.current) ActiveWidget = null;
        }
    };

    const fitToScreen = () => {
        if (!waveform.current?.isReady) return;

        // Reset zoom level
        waveform.current.zoom(0);
    };

    const zoomToWindow = () => {
        if (!waveform.current?.isReady) return;
        if (!windows[0] || windows.length > 1) return;

        // Select the only window
        const window = windows[0];

        const start = isNaN(window[0]) ? 0 : window[0];
        const end = isNaN(window[1]) ? waveform.current?.getDuration() ?? 0 : window[1];

        const duration = waveform.current.getDuration();

        // Calculate the middle of the window
        const windowDuration = end - start;
        const midTime = start + windowDuration / 2;
        const midPercent = midTime / duration;

        // How much of the waveform is covered by the window?
        const windowPercentage = windowDuration / duration;
        const containerWidth = wavesurferContainer.current?.clientWidth ?? 0;

        // Total pixels per second
        const pxPerSec = containerWidth / duration;

        // Pixels per second of the window
        const pxPerSecWindow = (containerWidth * windowPercentage) / duration;

        // Leave 10% of container edges empty (left and right of window)
        const zoomRatio = (0.9 * pxPerSec) / pxPerSecWindow;

        // Zoom to middle
        waveform.current.zoom(Math.min(pxPerSec * zoomRatio, MAX_ZOOM));

        // Center waveform around middle
        waveform.current.drawer.recenter(midPercent);
    };

    const zoom = (event: WheelEvent<HTMLDivElement>) => {
        if (!waveform.current) return;
        if (!wavesurferContainer.current) return;

        const wf = waveform.current;

        event.stopPropagation();

        const boundingRect = wavesurferContainer.current.getBoundingClientRect();

        // Position of mouse cursor, relative to left container border
        const cursorX = event.clientX - boundingRect.x;

        // 'Invisible' scrolled part to the left
        const offsetLeft = wf.drawer.wrapper.scrollLeft;

        // Pixel position of the cursor, relative to scrolled waveform
        const cursorPx = cursorX + offsetLeft;

        // Cursor position normalized to waveform size
        const cursorNorm = cursorPx / wf.drawer.wrapper.scrollWidth;

        const maxZoom = 2500;

        const containerWidth = boundingRect.width;

        // Total pixels per second -> zoom level 1
        const pxPerSec = containerWidth / waveform.current.getDuration();

        wf.params.minPxPerSec = Math.max(
            pxPerSec,
            Math.min(wf.params.minPxPerSec - event.deltaY, maxZoom)
        );
        wf.params.scrollParent = true;
        wf.drawBuffer();
        wf.drawer.progress(wf.backend.getPlayedPercents());

        // ScrollWidth is slightly different after zoom
        const newCursorPx = cursorNorm * wf.drawer.wrapper.scrollWidth;

        // Calculate offset from cursor to container center
        const cursorToCenter =
            wf.drawer.wrapper.getBoundingClientRect().width / 2 - cursorX;

        // New center is offset + updated cursor pixel position
        const newCenterPx = cursorToCenter + newCursorPx;

        if (wf.params.minPxPerSec < MAX_ZOOM)
            wf.drawer.recenterOnPosition(newCenterPx, true);

        wf.fireEvent('zoom', wf.params.minPxPerSec);
    };

    return (
        <Container>
            <div
                ref={wavesurferContainer}
                onWheel={zoom}
                tw="flex-grow overflow-hidden relative"
            >
                <WaveStyles ref={wavesurferElement} tw="h-full w-full">
                    {url ? '' : <EmptyNote>No Data</EmptyNote>}
                </WaveStyles>
            </div>
            <svg ref={timelineContainer} height="16">
                <g />
            </svg>
            {showControls && (
                <Toolbar>
                    {windows !== undefined && (
                        <ToolbarButton
                            tooltip="Play Region"
                            onClick={playRegion}
                            disabled={
                                !windows[0] || windows.length > 1 || url === undefined
                            }
                        >
                            <BsPlayCircleFill />
                        </ToolbarButton>
                    )}
                    <ToolbarButton
                        tooltip="Play/Pause"
                        onClick={playPause}
                        disabled={url === undefined}
                    >
                        {isPlaying ? <BsPauseCircle /> : <BsPlayCircle />}
                    </ToolbarButton>
                    <ToolbarButton
                        tooltip="Stop"
                        onClick={stopPlaying}
                        disabled={url === undefined}
                    >
                        <BsStopCircle />
                    </ToolbarButton>
                    <div tw="flex-grow" />
                    <ToolbarButton
                        tooltip="Zoom to window"
                        onClick={zoomToWindow}
                        disabled={url === undefined}
                    >
                        <ResetIcon />
                    </ToolbarButton>
                    <ToolbarButton
                        tooltip="Fit screen"
                        onClick={fitToScreen}
                        disabled={url === undefined}
                    >
                        <MaximizeIcon />
                    </ToolbarButton>
                    <ToolbarButton
                        tooltip="Repeat"
                        checked={repeat}
                        onClick={toggleRepeat}
                    >
                        <RepeatIcon />
                    </ToolbarButton>
                </Toolbar>
            )}
            {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
            <audio ref={audioRef} src={url} />
        </Container>
    );
};

export default AudioViewer;

import React, { ComponentProps, useRef, useState } from 'react';
import { BsPauseCircle, BsPlayCircle, BsStopCircle } from 'react-icons/bs';
import ReactPlayer from 'react-player';
import tw, { styled, theme } from 'twin.macro';
import BaseButton from '../components/ui/Button';
import ToggleButton from '../components/ui/ToggleButton';
import { Lens, LensProps } from './types';

type ProgressCallback = ComponentProps<typeof ReactPlayer>['onProgress'];

/*
 * No types available for these modules:
 */
const Container = tw.div`flex flex-col w-full h-full items-stretch overflow-hidden`;
const Toolbar = tw.div`flex flex-row items-center p-1`;
const VideoWrapper = tw.div`w-full h-full overflow-hidden`;
const Note = styled.p`
    color: ${theme`colors.gray.500`};
    ${tw`flex h-full items-center justify-center`}
`;

// Pause functionality is only available at runtime
// and setting the 'isPlaying' state alone does not stop the active
// player from playing, hence this interface.
// See https://github.com/cookpete/react-player/issues/1085
// for an explanation.
interface VideoPlayer extends ReactPlayer {
    pause: () => void;
    player: VideoPlayer;
}

// Only one active widget at a time
let ActivePlayer: VideoPlayer | null;

/*
 * Draws a new timeline
 */
const VideoView: Lens = ({ url }: LensProps) => {
    const videoContainer = useRef<HTMLDivElement>(null);
    const videoPlayer = useRef<VideoPlayer>(null);

    const [isPlaying, setIsPlaying] = useState(false);
    const [isSeeking, setIsSeeking] = useState(false);
    const [played, setPlayed] = useState(0);
    const [unsupported, setUnsupported] = useState(false);
    const [duration, setDuration] = useState(0);

    const format = (seconds: number) => {
        const date = new Date(seconds * 1000);
        const hh = date.getUTCHours();
        const mm = date.getUTCMinutes();
        const ss = pad(date.getUTCSeconds());
        if (hh) {
            return `${hh}:${pad(mm)}:${ss}`;
        }
        return `${mm}:${ss}`;
    };

    const pad = (string: number) => {
        return ('0' + string).slice(-2);
    };

    const handleProgress: ProgressCallback = ({ played }) => {
        // We only want to update time slider if we are not currently seeking
        if (!isSeeking) {
            setPlayed(played);
        }
    };

    const handleOnDuration = (e: number) => {
        setDuration(e);
    };

    const handleSeekMouseDown = () => {
        setIsSeeking(true);
    };

    const handleSeekMouseUp = (e: React.FormEvent<HTMLInputElement>) => {
        setIsSeeking(false);
        setPlayed(parseFloat(e.currentTarget.value));
        videoPlayer.current?.seekTo(played);
    };

    const handleSeekChange = (e: React.FormEvent<HTMLInputElement>) => {
        setPlayed(parseFloat(e.currentTarget.value));
        videoPlayer.current?.seekTo(played);
    };

    const handlePause = () => {
        setIsPlaying(false);
    };

    const handleOnError = () => {
        setUnsupported(true);
    };

    /*
     * Player controls
     */
    const playPause = () => {
        if (videoPlayer.current == null) return;

        if (ActivePlayer !== videoPlayer.current) {
            // Another widget is playing but play was pressed here
            // therefore pause active player and overwrite with this

            if (ActivePlayer) ActivePlayer?.player?.player.pause();

            // Set this widget active
            ActivePlayer = videoPlayer.current;
        }

        setIsPlaying(!isPlaying);
    };

    const stopPlaying = () => {
        videoPlayer.current?.seekTo(0);
        setIsPlaying(false);
        ActivePlayer = null;
    };

    return (
        <Container ref={videoContainer}>
            {url === undefined ? (
                <Note>No Data</Note>
            ) : unsupported ? (
                <Note>Unsupported Format</Note>
            ) : (
                <VideoWrapper style={{ background: theme`colors.black` }}>
                    <ReactPlayer
                        playing={isPlaying}
                        ref={videoPlayer}
                        height="100%"
                        width="100%"
                        onError={handleOnError}
                        onPause={handlePause}
                        onProgress={handleProgress}
                        onDuration={handleOnDuration}
                        url={url}
                    ></ReactPlayer>
                </VideoWrapper>
            )}
            <Toolbar>
                <ToggleButton
                    tooltip="Play/Pause"
                    tw="flex-none flex items-center"
                    onChange={playPause}
                    disabled={url === undefined || unsupported}
                >
                    {isPlaying ? <BsPauseCircle /> : <BsPlayCircle />}
                </ToggleButton>
                <BaseButton
                    tooltip="Stop"
                    tw="flex-none flex items-center"
                    onClick={stopPlaying}
                    disabled={url === undefined || unsupported}
                >
                    <BsStopCircle />
                </BaseButton>
                <input
                    type="range"
                    min={0}
                    max={0.999999}
                    step="any"
                    value={played}
                    onMouseDown={handleSeekMouseDown}
                    onChange={handleSeekChange}
                    onMouseUp={handleSeekMouseUp}
                    disabled={url === undefined || unsupported}
                    tw="flex-1 min-w-0"
                />
                <p tw="text-xs px-1">
                    {format(duration * played) + '/' + format(duration)}
                </p>
            </Toolbar>
        </Container>
    );
};

VideoView.defaultHeight = 256;
VideoView.displayName = 'Video Player';
VideoView.dataTypes = ['Video'];

export default VideoView;

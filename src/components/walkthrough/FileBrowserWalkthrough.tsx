import usePersistentState from '../../hooks/usePersistentState';
import React, { useCallback, useImperativeHandle } from 'react';
import { ACTIONS, STATUS } from 'react-joyride';
import type { CallBackProps, Step } from 'react-joyride';
import 'twin.macro';
import Tour from './Tour';

const TOUR_STEPS: Step[] = [
    {
        target: '[data-tour="openTableFileDialog"]',
        content: 'In order to use Spotlight first select a valid h5 dataset to load.',
        disableBeacon: true,
    },
];

export type Handle = {
    restartTour: () => void;
};

const Walkthrough: React.ForwardRefRenderFunction<Handle> = (_, ref) => {
    const [didRun, setWalkthroughState, walkthroughStatePending] = usePersistentState(
        'walkthrough.filebrowser_tour.did_run',
        false
    );

    useImperativeHandle(
        ref,
        () => ({
            restartTour: () => {
                setWalkthroughState(false);
            },
        }),
        [setWalkthroughState]
    );

    const tourCallback = useCallback(
        ({ action, status }: CallBackProps) => {
            if (
                action === ACTIONS.CLOSE ||
                (status === STATUS.SKIPPED && !didRun) ||
                status === STATUS.FINISHED
            ) {
                setWalkthroughState(true);
            }
        },
        [didRun, setWalkthroughState]
    );

    return (
        <Tour
            steps={TOUR_STEPS}
            run={!walkthroughStatePending && !didRun}
            callback={tourCallback}
            disableOverlayClose={true}
            showProgress={false}
        />
    );
};

export default React.forwardRef(Walkthrough);

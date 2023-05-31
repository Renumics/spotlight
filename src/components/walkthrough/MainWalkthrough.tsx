import Docs from '../../icons/Docs';
import TourIcon from '../../icons/Tour';
import usePersistentState from '../../hooks/usePersistentState';
import React, { useCallback, useImperativeHandle } from 'react';
import { ACTIONS, STATUS } from 'react-joyride';
import type { CallBackProps, Step } from 'react-joyride';
import { Dataset, useDataset } from '../../stores/dataset';
import 'twin.macro';
import Tour from './Tour';

const TOUR_STEPS: Step[] = [
    {
        target: '[data-tour="fileBrowser"]',
        content: 'To load a different Dataset simply open it via the file browser.',
        disableBeacon: true,
    },
    {
        target: '[data-tour="filterBar"]',
        content: (
            <p>
                You can <b>filter</b> your Dataset based on column values or on active
                selections.
            </p>
        ),
        placement: 'right',
    },
    {
        target: '.flexlayout__tab',
        content: (
            <>
                <p>
                    Spotlight offers <b>different views</b> on your Dataset.
                </p>
                <p>
                    Each view provides a different perspective on your data and is{' '}
                    <b>synchronized</b> with all the other views.
                </p>
            </>
        ),
    },
    {
        target: '[data-tour="addWidget"]',
        content: (
            <>
                <p>
                    You can add more views via the <b>+</b>.
                </p>
                <p>To arrange the tabs simply use drag&apos;sn&apos;drop.</p>
            </>
        ),
        placement: 'right',
    },
    {
        target: '[data-tour="detailViewAddView"]',
        content: (
            <>
                <p>
                    The Details View provides different views on specific columns of{' '}
                    <b>selected data points</b>.
                </p>
                <p>
                    To <b>add</b> a view simply add it by clicking the Add View button.
                </p>
                <p>In order to see detailes of a row, select it in any other view.</p>
            </>
        ),
        placement: 'left',
    },
    {
        target: '[data-tour="helpButton"]',
        content: (
            <>
                <p>You can find further assistance through the help menu.</p>
                <p>
                    <TourIcon style={{ width: 15, height: 15 }} /> restarts the tour
                </p>
                <p>
                    <Docs style={{ width: 15, height: 15 }} /> opens the documentation
                </p>
            </>
        ),
    },
];

export type Handle = {
    restartTour: () => void;
};

const filenameSelector = (d: Dataset) => d.filename;

const Walkthrough: React.ForwardRefRenderFunction<Handle> = (_, ref) => {
    const filename = useDataset(filenameSelector);

    const [didRun, setDidRun, didRunPending] = usePersistentState(
        'walkthrough.main_tour.did_run',
        false
    );

    useImperativeHandle(
        ref,
        () => ({
            restartTour: () => {
                setDidRun(false);
            },
        }),
        [setDidRun]
    );

    const tourCallback = useCallback(
        ({ action, status }: CallBackProps) => {
            if (
                action === ACTIONS.CLOSE ||
                (status === STATUS.SKIPPED && !didRun) ||
                status === STATUS.FINISHED
            ) {
                setDidRun(true);
            }
        },
        [didRun, setDidRun]
    );

    return (
        <Tour
            steps={TOUR_STEPS}
            run={!!filename && !didRunPending && !didRun}
            continuous={true}
            callback={tourCallback}
            disableOverlayClose={true}
            showProgress={false}
        />
    );
};

export default React.forwardRef(Walkthrough);

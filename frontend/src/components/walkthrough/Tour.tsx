import type { ComponentProps, FunctionComponent } from 'react';
import ReactJoyride from 'react-joyride';
import { theme } from 'twin.macro';

type JoyrideProps = ComponentProps<typeof ReactJoyride>;

// one of joyride's dependencies tries to access
// stuff under global.*,
// but this is not available in modern browsers.
// For now, just redirect to globalThis.
window.global = globalThis;

const Tour: FunctionComponent<JoyrideProps> = (props) => {
    return (
        <ReactJoyride
            styles={{
                options: {
                    primaryColor: theme`colors.green.600`,
                    textColor: theme`colors.midnight.600`,
                    overlayColor: theme`colors.gray.900`,
                    beaconSize: 30,
                },
                tooltip: {
                    fontSize: theme`fontSize.base`,
                    padding: theme`padding.1`,
                },
                tooltipContent: {
                    paddingLeft: theme`padding.3`,
                    paddingBottom: theme`margin.2`,
                    paddingTop: theme`padding.2`,
                    textAlign: 'start',
                },
                tooltipFooter: {
                    marginTop: theme`margin.2`,
                },
                buttonClose: {
                    height: theme`height[2.5]`,
                    width: theme`width[2.5]`,
                    padding: theme`padding.2`,
                    strokeWidth: 1,
                    stroke: theme`colors.midnight.600`,
                    fill: theme`colors.midnight.600`,
                },
                buttonSkip: {
                    color: theme`colors.gray.700`,
                },
            }}
            locale={{
                back: 'Back',
                close: 'Close',
                last: 'Done',
                next: 'Next',
                open: 'Open the dialog',
                skip: 'Skip Tour',
            }}
            hideCloseButton={true}
            showSkipButton={true}
            showProgress={true}
            {...props}
        />
    );
};

export default Tour;

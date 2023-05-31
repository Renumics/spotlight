import * as React from 'react';
import { useMemo } from 'react';
import 'tippy.js/dist/tippy.css';
import tw from 'twin.macro';
import Popup from './Popup';

interface Props {
    content?: React.ReactNode;
    visible?: boolean;
    followCursor?: boolean;
    reference?: React.RefObject<Element>;
    borderless?: boolean;
    delay?: number | [number, number];
    duration?: number | [number, number];
    disabled?: boolean;
    children?: React.ReactNode;
    placement?: React.ComponentProps<typeof Popup>['placement'];
}

const Tooltip = ({
    content,
    visible,
    followCursor = false,
    reference,
    borderless = false,
    delay = [500, 0],
    duration = 100,
    disabled = false,
    children,
    placement,
}: Props): JSX.Element => {
    const wrappedContent = useMemo(
        () => (
            <div css={[!borderless && tw`p-0.5`, tw`min-w-[24px] text-center`]}>
                {content}
            </div>
        ),
        [content, borderless]
    );

    return (
        <Popup
            content={wrappedContent}
            disabled={disabled || !content}
            visible={visible}
            delay={delay}
            duration={duration}
            followCursor={followCursor}
            reference={reference}
            placement={placement}
        >
            {children}
        </Popup>
    );
};

export default Tooltip;

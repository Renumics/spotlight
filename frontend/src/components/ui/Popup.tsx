import Tippy from '@tippyjs/react';
import * as React from 'react';
import { ComponentProps, FunctionComponent, useCallback } from 'react';
import { followCursor as followCursorPlugin } from 'tippy.js';
import type { Instance, Placement } from 'tippy.js';
import 'tippy.js/dist/tippy.css';
import tw, { styled, theme } from 'twin.macro';

type TippyProps = ComponentProps<typeof Tippy>;

interface Props {
    content?: React.ReactNode;
    visible?: boolean;
    followCursor?: boolean;
    reference?: React.RefObject<Element>;
    delay?: number | [number, number];
    duration?: number | [number, number];
    disabled?: boolean;
    className?: string;
    placement?: Placement;
    interactive?: boolean;
    offset?: [number, number];
    onShow?: TippyProps['onShow'];
    onMount?: TippyProps['onMount'];
    onHide?: TippyProps['onHide'];
    onClickOutside?: TippyProps['onClickOutside'];
    children: React.ReactNode;
}

const arrowColor = theme`colors.gray.100`;

const StyledTippy = styled(Tippy)`
    ${tw`
        bg-gray-100!
        border!
        rounded!
        border-gray-400!
        shadow-md!
        text-sm!
        text-midnight-600!
    `};

    .tippy-content {
        ${tw`m-0 p-0 max-h-[600px] overflow-auto`}
    }

    .tippy-arrow::before {
        display: block;
        z-index: -1;
        content: '';
        border-left: 7px solid transparent;
        border-right: 7px solid transparent;
        border-top: 7px solid transparent;
        border-bottom: 7px solid transparent;
    }

    &[data-placement^='bottom'] {
        .tippy-arrow {
            top: 0;
        }
        .tippy-arrow::before {
            border-bottom-color: ${arrowColor} !important;
        }
    }

    &[data-placement^='top'] {
        .tippy-arrow {
            bottom: 0;
        }
        .tippy-arrow::before {
            border-top-color: ${arrowColor} !important;
        }
    }

    &[data-placement^='left'] {
        .tippy-arrow {
            right: 0;
        }
        .tippy-arrow::before {
            border-left-color: ${arrowColor} !important;
        }
    }

    &[data-placement^='right'] {
        .tippy-arrow {
            right: 0;
        }
        .tippy-arrow::before {
            border-right-color: ${arrowColor} !important;
        }
    }
`;

function doNothing() {
    // do nothing
}

const plugins = [followCursorPlugin];

const Popup: FunctionComponent<Props> = ({
    content,
    visible,
    followCursor = false,
    reference,
    delay,
    duration = 100,
    children,
    className,
    disabled,
    placement = 'top',
    interactive,
    onMount = doNothing,
    onShow = doNothing,
    onHide = doNothing,
    offset = [0, 8],
    onClickOutside = doNothing,
}) => {
    const handleClickOutside = useCallback(
        (instance: Instance, event: Event) => {
            const selectMenuRoot = document.getElementById('selectMenuRoot');
            if (!selectMenuRoot?.contains(event.target as HTMLElement)) {
                onClickOutside(instance, event);
            }
        },
        [onClickOutside]
    );

    return (
        <StyledTippy
            appendTo={document.body}
            theme="light-border"
            className={className}
            content={content}
            disabled={disabled}
            visible={visible}
            delay={delay}
            duration={duration}
            maxWidth="none"
            animation="fade"
            followCursor={followCursor}
            reference={reference}
            plugins={plugins}
            placement={placement}
            interactive={interactive}
            onClickOutside={handleClickOutside}
            onMount={onMount}
            onShow={onShow}
            onHide={onHide}
            offset={offset}
        >
            <div>{children}</div>
        </StyledTippy>
    );
};

export default Popup;

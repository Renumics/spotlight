import Tippy, { useSingleton } from '@tippyjs/react';
import type { TippyProps } from '@tippyjs/react';
import * as React from 'react';
import { FunctionComponent, useCallback, useContext, useRef, useState } from 'react';
import { followCursor } from 'tippy.js';
import tw, { styled } from 'twin.macro';

const StyledTippy = styled(Tippy)`
    ${tw`
        m-0!
        p-0!
        bg-gray-100!
        border!
        border-gray-400!
        shadow-md!
        rounded-none!
        text-xs!
        text-midnight-600!
    `}

    .tippy-content {
        ${tw`m-0 p-0 py-0.5`}
    }
`;

type ContextMenuContextState = {
    _target?: ReturnType<typeof useSingleton>[1];
    _mountedRef: EventTarget | null;
    hide: () => void;
    show: () => void;
};

const ContextMenuContext = React.createContext<ContextMenuContextState>({
    _target: undefined,
    _mountedRef: null,
    hide: () => null,
    show: () => null,
});

export const ContextMenuProvider: FunctionComponent<{ children: React.ReactNode }> = ({
    children,
}) => {
    const [source, target] = useSingleton();
    const [mountedRef, setMountedRef] = useState<EventTarget | null>(null);

    const hide = useCallback(() => {
        source?.data?.instance?.hide();
    }, [source?.data?.instance]);

    const show = useCallback(() => {
        source?.data?.instance?.show();
    }, [source?.data?.instance]);

    const onTrigger = useCallback((_: unknown, event: Event) => {
        setMountedRef(event.currentTarget);
    }, []);

    const onHidden = useCallback(() => {
        setMountedRef(null);
    }, []);

    return (
        <ContextMenuContext.Provider
            value={{
                _target: target,
                _mountedRef: mountedRef,
                hide,
                show,
            }}
        >
            <StyledTippy
                appendTo={document.body}
                singleton={source}
                onTrigger={onTrigger}
                onHidden={onHidden}
                placement={'bottom-start'}
                trigger={'contextmenu'}
                interactive={true}
                followCursor={'initial'}
                hideOnClick={true}
                onClickOutside={hide}
                plugins={[followCursor]}
                role={'menu'}
                arrow={false}
                duration={0}
            />
            {children}
        </ContextMenuContext.Provider>
    );
};

const ContextMenu: FunctionComponent<Pick<TippyProps, 'content' | 'children'>> = ({
    content,
    children,
}) => {
    const { _target, _mountedRef } = useContext(ContextMenuContext);
    const ref = useRef<HTMLDivElement>(null);

    return (
        <StyledTippy
            singleton={_target}
            content={_mountedRef === ref.current ? content : <></>}
        >
            <div ref={ref}>{children}</div>
        </StyledTippy>
    );
};

export const useContextMenu = (): Omit<
    ContextMenuContextState,
    '_mountedRef' | '_target'
> => {
    const { show, hide } = useContext(ContextMenuContext);
    return { show, hide };
};

export default ContextMenu;

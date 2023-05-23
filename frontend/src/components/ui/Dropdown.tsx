import {
    autoUpdate,
    flip,
    FloatingPortal,
    offset,
    shift,
    size,
    useClick,
    useDismiss,
    useFloating,
    useInteractions,
} from '@floating-ui/react';
import Button from './Button';
import useOnClickOutside from '../../hooks/useOnClickOutside';
import usePrevious from '../../hooks/usePrevious';
import {
    createContext,
    ReactNode,
    useCallback,
    useEffect,
    useLayoutEffect,
    useRef,
    useState,
} from 'react';
import 'twin.macro';

interface Props {
    content?: ReactNode;
    tooltip?: ReactNode;
    children?: ReactNode;
    onHide?: () => void;
    onShow?: () => void;
    className?: string;
}

export const DropdownContext = createContext({
    visible: false,
    show: () => {
        //doNothing
    },
    hide: () => {
        //doNothing
    },
});

const Dropdown = ({
    content,
    tooltip,
    children,
    onShow,
    onHide,
    className,
}: Props): JSX.Element => {
    const [open, setOpen] = useState(false);
    const floatingRef = useRef<HTMLElement>(null);
    const referenceRef = useRef<HTMLElement>(null);

    const { context, x, y, strategy, floating, reference } = useFloating({
        open,
        onOpenChange: setOpen,
        whileElementsMounted: (reference, floating, update) =>
            autoUpdate(reference, floating, update, {
                animationFrame: true,
            }),
        middleware: [
            offset(2),
            shift(),
            flip(),
            size({
                apply({ availableHeight, elements }) {
                    Object.assign(elements.floating.style, {
                        maxHeight: `${availableHeight}px`,
                    });
                },
            }),
        ],
    });
    const { getReferenceProps, getFloatingProps } = useInteractions([
        useClick(context, {}),
        useDismiss(context, {
            escapeKey: true,
            outsidePress: true,
        }),
    ]);

    const wasOpen = usePrevious(open);
    useEffect(() => {
        if (open && !wasOpen) {
            onShow?.();
        } else if (!open && wasOpen) {
            onHide?.();
        }
    }, [open, wasOpen, onShow, onHide]);

    const show = useCallback(() => {
        setOpen(true);
    }, []);
    const hide = useCallback(() => {
        setOpen(false);
    }, []);
    const dropdownContext = { show, hide, visible: open };

    useLayoutEffect(() => {
        reference(referenceRef.current);
    }, [reference]);

    useLayoutEffect(() => {
        if (!floatingRef.current) return;
        floating(floatingRef.current);
    }, [floating, open]);

    useOnClickOutside(floatingRef, (event) => {
        if (event.target && referenceRef.current?.contains(event.target as HTMLElement))
            return;

        if (open) hide();
    });

    return (
        <>
            <Button
                {...getReferenceProps({
                    ref: referenceRef,
                })}
                tooltip={tooltip}
                className={className}
            >
                {children}
            </Button>
            <FloatingPortal id="popupRoot">
                {open && (
                    <DropdownContext.Provider value={dropdownContext}>
                        <div
                            tw="bg-gray-100 border border-gray-300 shadow-lg outline-none overflow-auto"
                            {...getFloatingProps({
                                ref: floatingRef,
                                style: {
                                    position: strategy,
                                    left: x ?? 0,
                                    top: y ?? 0,
                                },
                            })}
                        >
                            {content}
                        </div>
                    </DropdownContext.Provider>
                )}
            </FloatingPortal>
        </>
    );
};

export default Dropdown;

import { MouseEvent, ReactNode, useCallback, useRef } from 'react';
import ReactDOM from 'react-dom';
import tw, { styled } from 'twin.macro';

type Props = {
    onClickOutside?: () => void;
    isVisible?: boolean;
    children: ReactNode;
    title?: string;
    className?: string;
};

const DialogWrapper = styled.div`
    ${tw`bg-gray-100 rounded shadow-md`};
    max-width: 75vw;
`;
const DialogBackground = tw.div`w-screen h-screen bg-midnight-600/50 flex place-content-around items-center`;

const Dialog = ({
    className,
    isVisible,
    children,
    onClickOutside = () => null,
}: Props): JSX.Element => {
    const ref = useRef(null);
    const onClick = useCallback(
        (event: MouseEvent<HTMLDivElement>) => {
            if (event.target === ref.current) onClickOutside();
        },
        [onClickOutside]
    );

    if (!isVisible) return <></>;

    const DialogRoot = document.getElementById('modalRoot');
    if (DialogRoot === null) return <></>;

    return ReactDOM.createPortal(
        <DialogBackground className={className} ref={ref} onClick={onClick}>
            <DialogWrapper>{children}</DialogWrapper>
        </DialogBackground>,
        DialogRoot
    );
};

export default Dialog;

import { FunctionComponent, ReactNode } from 'react';
import ReactDOM from 'react-dom';
import tw, { styled } from 'twin.macro';
import Button from './Button';

type Props = {
    isVisible?: boolean;
    title?: string;
    message?: string;
    onAccept?: () => void;
    acceptText?: string;
    onCancel?: () => void;
    cancelText?: string;
    children?: ReactNode;
};

const DialogBackground = tw.div`w-screen h-screen bg-gray-900 bg-opacity-50 flex place-content-around items-center`;
const DialogWrapper = styled.div`
    ${tw`bg-gray-100 rounded shadow-md`}
    max-width: 400px;
`;
const DialogTitleWrapper = tw.div`flex text-sm text-gray-900 bg-gray-100 border-b-2 px-2 pb-1 mt-2 font-semibold`;
const DialogTextWrapper = tw.div`flex text-sm text-gray-900 px-2 pb-2 mt-2`;
const DialogButtonWrapper = tw.div`flex place-content-end bg-gray-200 space-x-2 p-1 px-2 rounded`;

const StyledAcceptButton = styled(Button)`
    ${tw`bg-red-400 border-red-400 hover:(bg-red-600 border-red-600) text-white text-sm hover:text-white rounded px-2 uppercase`}
`;

const AcceptButton = ({
    onAccept,
    acceptText = 'ok',
}: {
    onAccept?: () => void;
    acceptText?: string;
}) => (
    <StyledAcceptButton outlined={true} onClick={onAccept}>
        {acceptText}
    </StyledAcceptButton>
);

const StyledCancelButton = styled(Button)`
    ${tw`text-gray-800 hover:text-gray-900 text-sm rounded px-2 uppercase`}
`;

const CancelButton = ({
    onCancel,
    cancelText = 'cancel',
}: {
    onCancel?: () => void;
    cancelText?: string;
}) => (
    <StyledCancelButton outlined={true} onClick={onCancel}>
        {cancelText}
    </StyledCancelButton>
);

const ConfirmationDialog: FunctionComponent<Props> = ({
    isVisible,
    title,
    onAccept,
    acceptText,
    onCancel,
    cancelText,
    children,
}) => {
    if (!isVisible) return <></>;

    const DialogRoot = document.getElementById('modalRoot');
    if (DialogRoot === null) return <></>;

    return ReactDOM.createPortal(
        <DialogBackground>
            <DialogWrapper>
                {title && <DialogTitleWrapper>{title}</DialogTitleWrapper>}
                <DialogTextWrapper>{children}</DialogTextWrapper>
                <DialogButtonWrapper>
                    <CancelButton onCancel={onCancel} cancelText={cancelText} />
                    <AcceptButton onAccept={onAccept} acceptText={acceptText} />
                </DialogButtonWrapper>
            </DialogWrapper>
        </DialogBackground>,
        DialogRoot
    );
};

export default ConfirmationDialog;

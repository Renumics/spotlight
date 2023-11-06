import FilterBar from './FilterBar';
import LayoutIcon from '../icons/Layout';
import LoadIcon from '../icons/OpenFolder';
import ResetLayoutIcon from '../icons/ResetLayout';
import SaveIcon from '../icons/Save';
import Button from './ui/Button';
import {
    ChangeEvent,
    FunctionComponent,
    useCallback,
    useContext,
    useRef,
    useState,
} from 'react';
import tw, { styled } from 'twin.macro';
import ConfirmationDialog from './ui/ConfirmationDialog';
import Dropdown, { DropdownContext } from './ui/Dropdown';
import Menu from './ui/Menu';

const StyledDiv = styled.div`
    ${tw`w-full z-10 flex items-center bg-gray-200 pr-0.5`}
`;

interface ResetLayoutProps {
    visible: boolean;
    hide: () => void;
    resetWorkspace: () => void;
}

const ResetDialog = ({ resetWorkspace, visible, hide }: ResetLayoutProps) => {
    const onAccept = useCallback(() => {
        hide();
        resetWorkspace();
    }, [resetWorkspace, hide]);

    return (
        <>
            <ConfirmationDialog
                title="Reset Layout?"
                isVisible={visible}
                onAccept={onAccept}
                onCancel={hide}
                acceptText={'reset'}
            >
                Are you sure you want to reset the layout?
            </ConfirmationDialog>
        </>
    );
};

interface ResetLayoutButtonProps {
    show: () => void;
}
const ResetLayoutButton = ({ show }: ResetLayoutButtonProps): JSX.Element => {
    const { hide: hideDropdown } = useContext(DropdownContext);

    const handleClick = useCallback(() => {
        hideDropdown();
        show();
    }, [show, hideDropdown]);

    return (
        <Button
            tw="flex flex-row whitespace-nowrap flex-nowrap font-normal"
            tooltip="Reset Layout"
            onClick={handleClick}
        >
            <ResetLayoutIcon tw="mr-1" />
            Reset Layout
        </Button>
    );
};

interface LoadLayoutButtonProps {
    loadLayout: (file: File) => void;
}

const LoadLayoutButton = ({ loadLayout }: LoadLayoutButtonProps): JSX.Element => {
    const inputRef = useRef<HTMLInputElement>(null);

    const { hide: hideDropdown } = useContext(DropdownContext);

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) loadLayout(file);
        e.target.value = '';
        hideDropdown();
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    return (
        <>
            <Button
                tw="flex flex-row whitespace-nowrap font-normal"
                onClick={handleClick}
            >
                <LoadIcon tw="mr-1" />
                Load Layout
            </Button>
            <input
                ref={inputRef}
                type="file"
                accept="application/json"
                onChange={handleChange}
                hidden={true}
            />
        </>
    );
};

interface SaveLayoutButtonProps {
    saveLayout: () => void;
}
const SaveLayoutButton = ({ saveLayout }: SaveLayoutButtonProps): JSX.Element => {
    return (
        <Button
            tw="flex flex-row whitespace-nowrap flex-nowrap font-normal"
            onClick={saveLayout}
        >
            <SaveIcon tw="mr-1" />
            Save Layout
        </Button>
    );
};

interface Props {
    resetWorkspace: () => void;
    saveLayout: () => void;
    loadLayout: (file: File) => void;
}

const ToolBar: FunctionComponent<Props> = ({
    resetWorkspace,
    saveLayout,
    loadLayout,
}): JSX.Element => {
    const [resetDialogVisible, setResetDialogVisible] = useState(false);

    const showResetDialog = useCallback(() => setResetDialogVisible(true), []);
    const hideResetDialog = useCallback(() => setResetDialogVisible(false), []);

    const dropdownContent = (
        <Menu tw="m-0.5">
            <Menu.Item>
                <LoadLayoutButton loadLayout={loadLayout} />
            </Menu.Item>
            <Menu.Item>
                <SaveLayoutButton saveLayout={saveLayout} />
            </Menu.Item>
            <Menu.Item>
                <ResetLayoutButton show={showResetDialog} />
            </Menu.Item>
        </Menu>
    );

    return (
        <StyledDiv>
            <FilterBar />
            <span tw="flex items-center">
                <Dropdown content={dropdownContent} tooltip="Layout">
                    <LayoutIcon />
                </Dropdown>
            </span>
            <ResetDialog
                visible={resetDialogVisible}
                hide={hideResetDialog}
                resetWorkspace={resetWorkspace}
            />
        </StyledDiv>
    );
};

export default ToolBar;

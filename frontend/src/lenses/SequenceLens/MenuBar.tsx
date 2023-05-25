import ResetIcon from '../../icons/Reset';
import SettingsIcon from '../../icons/Settings';
import Button from '../../components/ui/Button';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import { FunctionComponent } from 'react';
import tw from 'twin.macro';

const Styles = tw.div`px-2 py-1 absolute top-0 right-0 items-start flex flex-row-reverse`;

interface Props {
    groupY: boolean;
    isXSynchronized: boolean;
    isYSynchronized: boolean;
    isXSyncedGlobally: boolean;
    onChangeGroupY: (show: boolean) => void;
    onReset: () => void;
    onChangeIsXSynchronized: (isSynchronized: boolean) => void;
    onChangeIsYSynchronized: (isSynchronized: boolean) => void;
    onChangeIsXSyncedGlobally: (isSyncedGlobally: boolean) => void;
}

const MenuBar: FunctionComponent<Props> = ({
    groupY,
    isXSynchronized,
    isYSynchronized,
    isXSyncedGlobally,
    onChangeGroupY,
    onReset,
    onChangeIsXSynchronized,
    onChangeIsYSynchronized,
    onChangeIsXSyncedGlobally,
}) => {
    const settingsMenu = (
        <Menu>
            <Menu.Title>Y-Axis</Menu.Title>
            <Menu.Switch value={groupY} onChange={onChangeGroupY}>
                Show Multiple
            </Menu.Switch>
            <Menu.Switch value={isYSynchronized} onChange={onChangeIsYSynchronized}>
                Synchronize
            </Menu.Switch>
            <Menu.Title>X-Axis</Menu.Title>
            <Menu.Switch value={isXSynchronized} onChange={onChangeIsXSynchronized}>
                Synchronize
            </Menu.Switch>
            <Menu.Switch value={isXSyncedGlobally} onChange={onChangeIsXSyncedGlobally}>
                Synchronize Globally
            </Menu.Switch>
        </Menu>
    );

    return (
        <Styles>
            <div data-test-tag="sequenceview-settings-dropdown">
                <Dropdown content={settingsMenu} tw="p-4">
                    <SettingsIcon />
                </Dropdown>
            </div>
            <Button onClick={onReset}>
                <ResetIcon />
            </Button>
        </Styles>
    );
};

export default MenuBar;

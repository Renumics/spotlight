import SettingsIcon from '../../../icons/Settings';
import Dropdown from '../../../components/ui/Dropdown';
import { default as MenuWrapper } from '../../../components/ui/Menu';
import { ChangeEvent, FunctionComponent, useCallback } from 'react';
import { useOrderColumnsByRelevance } from '../context/columnContext';

const Content = (): JSX.Element => {
    const [columnsSortedByRelvance, setColumnsSortedByRelevance] =
        useOrderColumnsByRelevance();

    const onChangeColumnsSortedByRelevance = useCallback(
        (event: ChangeEvent<HTMLInputElement>) =>
            setColumnsSortedByRelevance(event.target.checked),
        [setColumnsSortedByRelevance]
    );

    return (
        <MenuWrapper>
            <MenuWrapper.Title>Order Columns</MenuWrapper.Title>
            <MenuWrapper.Item>
                <label>
                    <input
                        type="checkbox"
                        checked={columnsSortedByRelvance}
                        onChange={onChangeColumnsSortedByRelevance}
                    />
                    <span> by relevance</span>
                </label>
            </MenuWrapper.Item>
        </MenuWrapper>
    );
};

const SettingsButton: FunctionComponent = () => {
    return (
        <div data-test-tag="datagrid-settings-dropdown">
            <Dropdown content={<Content />} tooltip="Settings">
                <SettingsIcon />
            </Dropdown>
        </div>
    );
};

export default SettingsButton;

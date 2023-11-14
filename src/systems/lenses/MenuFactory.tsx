import { Fragment } from 'react';
import Menu from '../../components/ui/Menu';
import { Setting, Settings } from './types';

interface ItemProps {
    setting: Setting;
    onChange: (value: unknown) => void;
}

const ItemFactory = ({ setting, onChange }: ItemProps): JSX.Element => {
    const valueType = typeof setting.value;
    if (valueType === 'number' || valueType === 'string') {
        return <Menu.Input value={setting.value as number} onChange={onChange} />;
    }
    return <>{setting.value}</>;
};

interface Props {
    settings: Settings;
    onChange: (settings: Settings) => null;
}

const MenuFactory = ({ settings, onChange }: Props): JSX.Element => {
    const items = Object.entries(settings).map(([key, setting]) => (
        <Fragment key={key}>
            <Menu.Title>{key}</Menu.Title>
            <Menu.Item>
                <ItemFactory
                    setting={setting}
                    onChange={(value) => onChange({ key: { value } })}
                />
            </Menu.Item>
        </Fragment>
    ));
    return <Menu>{items}</Menu>;
};

export default MenuFactory;

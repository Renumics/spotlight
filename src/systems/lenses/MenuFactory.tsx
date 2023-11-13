import Menu from '../../components/ui/Menu';
import { Setting, Settings } from './types';

interface ItemProps {
    setting: Setting;
    onChange: (value: unknown) => void;
}

const ItemFactory = ({ setting, onChange }: ItemProps): JSX.Element => {
    return <>{setting.value}</>;
};

interface Props {
    settings: Settings;
    onChange: (settings: Settings) => null;
}

const MenuFactory = ({ settings, onChange }: Props): JSX.Element => {
    const items = Object.entries(settings).map(([key, setting]) => (
        <Menu.Item key={key}>
            <ItemFactory
                setting={setting}
                onChange={(value) => onChange({ key: { value } })}
            />
        </Menu.Item>
    ));
    return <Menu>{items}</Menu>;
};

export default MenuFactory;

import SettingsIcon from '../../../icons/Settings';
import Dropdown from '../../../components/ui/Dropdown';
import Menu from '../../../components/ui/Menu';
import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';

const Styles = styled.div`
    ${tw`z-10 px-2 py-1 absolute top-0 right-0 items-start flex flex-row-reverse`}
    button {
        ${tw`text-gray-100
        hover:text-gray-400
        active:hover:text-gray-200
        focus:text-gray-600
    `}
    }
`;

interface Props {
    className?: string;
    isLooping: boolean;
    shouldAutostart: boolean;
    onChangeLoop: (enabled: boolean) => void;
    onChangeAutostart: (enabled: boolean) => void;
}

const MenuBar: FunctionComponent<Props> = ({
    className,
    isLooping,
    shouldAutostart,
    onChangeLoop,
    onChangeAutostart,
}) => {
    const content = (
        <Menu>
            <Menu.Title>Player settings</Menu.Title>
            <Menu.Switch value={isLooping} onChange={onChangeLoop}>
                Loop
            </Menu.Switch>
            <Menu.Switch value={shouldAutostart} onChange={onChangeAutostart}>
                Autoplay
            </Menu.Switch>
        </Menu>
    );

    return (
        <Styles className={className}>
            <Dropdown content={content}>
                <SettingsIcon />
            </Dropdown>
        </Styles>
    );
};

export default MenuBar;

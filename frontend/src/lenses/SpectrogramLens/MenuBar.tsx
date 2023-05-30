import SettingsIcon from '../../icons/Settings';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';

const Styles = styled.div`
    ${tw`px-2 py-1 absolute top-0 right-0 items-start flex flex-row-reverse`}
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
    isLogScale: boolean;
    onToggleScale: (enabled: boolean) => void;
}

const MenuBar: FunctionComponent<Props> = ({
    className,
    isLogScale,
    onToggleScale,
}) => {
    const content = (
        <Menu>
            <Menu.Title>Scale</Menu.Title>
            <Menu.Switch value={isLogScale} onChange={onToggleScale}>
                Logarithmic
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

import SettingsIcon from '../../icons/Settings';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import Select from '../../components/ui/Select';
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
    availableScales: string[];
    scale: string;
    onChangeScale: (scale: string) => void;
}

const MenuBar: FunctionComponent<Props> = ({
    className,
    availableScales,
    scale,
    onChangeScale,
}) => {
    const selectScale = (newScale?: string | null) => onChangeScale(newScale || '');

    const content = (
        <Menu>
            <Menu.Title>Scale</Menu.Title>
            <Select
                onChange={selectScale}
                value={scale}
                options={[null, ...availableScales]}
            />
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

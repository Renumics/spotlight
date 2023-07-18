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
    availableFreqScales: string[];
    availableAmpScales: string[];
    freqScale: string;
    ampScale: string;
    onChangeFreqScale: (scale: string) => void;
    onChangeAmpScale: (scale: string) => void;
}

const MenuBar: FunctionComponent<Props> = ({
    className,
    availableFreqScales,
    availableAmpScales,
    freqScale,
    ampScale,
    onChangeFreqScale,
    onChangeAmpScale,
}) => {
    const selectFreqScale = (newFreqScale?: string | null) =>
        onChangeFreqScale(newFreqScale || '');
    const selectAmpScale = (newAmpScale?: string | null) =>
        onChangeAmpScale(newAmpScale || '');

    const content = (
        <Menu>
            <Menu.Title>Frequency Scale</Menu.Title>
            <Select
                onChange={selectFreqScale}
                value={freqScale}
                options={[null, ...availableFreqScales]}
            />
            <Menu.Title>Amplitude Scale</Menu.Title>
            <Select
                onChange={selectAmpScale}
                value={ampScale}
                options={[null, ...availableAmpScales]}
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

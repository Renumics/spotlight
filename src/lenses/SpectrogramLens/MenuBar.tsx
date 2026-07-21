import SettingsIcon from '../../icons/Settings';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import Select from '../../components/ui/Select';
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
    availableFreqScales: string[];
    availableAmpScales: string[];
    availableChannels: number[];
    freqScale: string;
    ampScale: string;
    channel: number;
    onChangeFreqScale: (scale: string) => void;
    onChangeAmpScale: (scale: string) => void;
    onChangeChannel: (channel: number) => void;
}

const MenuBar: FunctionComponent<Props> = ({
    className,
    availableFreqScales,
    availableAmpScales,
    availableChannels,
    freqScale,
    ampScale,
    channel,
    onChangeFreqScale,
    onChangeAmpScale,
    onChangeChannel,
}) => {
    const selectFreqScale = (newFreqScale?: string) =>
        onChangeFreqScale(newFreqScale || '');
    const selectAmpScale = (newAmpScale?: string) =>
        onChangeAmpScale(newAmpScale || '');
    const selectChannel = (newChannel?: number) => onChangeChannel(newChannel ?? 0);

    const content = (
        <Menu tw="w-32">
            <Menu.Title>Frequency Scale</Menu.Title>
            <Select
                onChange={selectFreqScale}
                value={freqScale}
                options={[...availableFreqScales]}
            />
            <Menu.Title>Amplitude Scale</Menu.Title>
            <Select
                onChange={selectAmpScale}
                value={ampScale}
                options={[...availableAmpScales]}
            />
            {availableChannels.length > 1 && (
                <>
                    <Menu.Title>Channel</Menu.Title>
                    <Select
                        onChange={selectChannel}
                        value={channel}
                        options={[...availableChannels]}
                        label={(v) => `${(v ?? 0) + 1}`}
                    />
                </>
            )}
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

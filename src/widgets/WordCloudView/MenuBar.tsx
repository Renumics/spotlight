import FilterIcon from '../../icons/Filter';
import FilterOffIcon from '../../icons/FilterOff';
import ResetIcon from '../../icons/Reset';
import SettingsIcon from '../../icons/Settings';
import Button from '../../components/ui/Button';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import { FunctionComponent, memo } from 'react';
import tw from 'twin.macro';
import Slider from '../../components/ui/Slider';
import LabeledSlider from '../../components/ui/LabeledSlider';
import Cloud from './Cloud';
import { ComponentProps } from 'react';
import Select from '../../components/ui/Select';

const MenuBarWrapper = tw.div`pl-2 py-0.5 absolute top-0 right-0 items-start flex flex-row-reverse text-sm`;

interface MenuProps {
    placeableColumns: string[];
    wordCloudBy?: string;
    filter: boolean;
    scaling: ComponentProps<typeof Cloud>['scaling'];
    onChangeScaling: (scaling: ComponentProps<typeof Cloud>['scaling']) => void;
    onChangeWordCloudolumn: (column: string) => void;
    onChangeFilter: (filter: boolean) => void;
    onReset: () => void;
    maxWordCount: number;
    minWordCount: number;
    wordCount: number;
    onChangeWordCount: (value: number) => void;
}

type Props = MenuProps;

const SettingsMenu = ({
    placeableColumns,
    wordCloudBy,
    onChangeWordCloudolumn,
    maxWordCount,
    minWordCount,
    wordCount,
    onChangeWordCount,
    scaling,
    onChangeScaling,
}: Omit<Props, 'onChangeFilter' | 'filter'>): JSX.Element => {
    return (
        <Menu tw="w-[360px]">
            <Menu.ColumnSelect
                title="Cloud By"
                onChangeColumn={onChangeWordCloudolumn}
                selectableColumns={placeableColumns}
                selected={wordCloudBy}
            />
            <Menu.Title>Reduction method</Menu.Title>
            <Menu.Item>
                <Select
                    value={scaling}
                    onChange={onChangeScaling}
                    options={['linear', 'log', 'sqrt']}
                />
            </Menu.Item>
            <Menu.Item>
                <Menu.Subtitle>Word Count</Menu.Subtitle>
                <LabeledSlider
                    showTooltip={true}
                    min={minWordCount}
                    max={maxWordCount}
                    onRelease={onChangeWordCount}
                    value={wordCount}
                />
            </Menu.Item>
        </Menu>
    );
};

const MenuBar: FunctionComponent<Props> = ({ filter, onChangeFilter, ...props }) => {
    const toggleFilter = () => onChangeFilter(!filter);

    return (
        <MenuBarWrapper>
            <Dropdown content={<SettingsMenu {...props} />} tooltip="Settings">
                <SettingsIcon />
            </Dropdown>
            <Button onClick={props.onReset} tooltip="Fit points">
                <ResetIcon />
            </Button>
            <Button
                onClick={toggleFilter}
                tooltip={filter ? 'show unfiltered' : 'hide unfiltered'}
            >
                {filter ? <FilterOffIcon /> : <FilterIcon />}
            </Button>
        </MenuBarWrapper>
    );
};

export default memo(MenuBar);

import FilterIcon from '../../icons/Filter';
import FilterOffIcon from '../../icons/FilterOff';
import ResetIcon from '../../icons/Reset';
import SettingsIcon from '../../icons/Settings';
import Button from '../../components/ui/Button';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import {
    FunctionComponent,
    memo,
    useCallback,
    useEffect,
    useState,
    ComponentProps,
} from 'react';
import tw from 'twin.macro';
import LabeledSlider from '../../components/ui/LabeledSlider';
import Cloud from './Cloud';
import Select from '../../components/ui/Select';
import _ from 'lodash';

const MenuBarWrapper = tw.div`pl-2 py-0.5 absolute top-0 right-0 items-start flex flex-row-reverse text-sm`;

export type BoolOpeartion =
    | 'difference'
    | 'intersection'
    | 'union'
    | 'symmetric difference';

interface MenuProps {
    placeableColumns: string[];
    wordCloudBy?: string;
    wordCloudCompareBy?: string;
    filter: boolean;
    scaling: ComponentProps<typeof Cloud>['scaling'];
    onChangeScaling: (scaling: ComponentProps<typeof Cloud>['scaling']) => void;
    onChangeWordCloudColumn: (column: string) => void;
    onChangeWordCloudCompareColumn: (column: string) => void;
    onChangeFilter: (filter: boolean) => void;
    onReset: () => void;
    maxWordCount: number;
    minWordCount: number;
    minWordLength: number;
    maxWordLength: number;
    onChangeMinWordLength: (value: number) => void;
    wordCount: number;
    onChangeWordCount: (value: number) => void;
    blacklist: string[];
    onChangeBlacklist: (values: string[]) => void;
    boolOperation: BoolOpeartion;
    onChangeBoolOperation: (operation?: BoolOpeartion) => void;
}

type Props = MenuProps;

const SettingsMenu = ({
    placeableColumns,
    wordCloudBy,
    wordCloudCompareBy,
    onChangeWordCloudColumn,
    onChangeWordCloudCompareColumn,
    maxWordCount,
    minWordCount,
    wordCount,
    onChangeWordCount,
    scaling,
    onChangeScaling,
    onChangeBlacklist,
    blacklist,
    boolOperation,
    onChangeBoolOperation,
    minWordLength,
    maxWordLength,
    onChangeMinWordLength,
}: Omit<Props, 'onChangeFilter' | 'filter'>): JSX.Element => {
    const [blacklistInputValue, setBlacklistInputValue] = useState(
        blacklist.join(', ')
    );
    const onChangeBlacklistInput = useCallback(() => {
        const newList = blacklistInputValue.split(/[\s,;]+/);
        if (!_.isEqual(newList, blacklist)) {
            onChangeBlacklist(newList);
        }
    }, [blacklist, blacklistInputValue, onChangeBlacklist]);

    useEffect(() => {
        setBlacklistInputValue(blacklist.join(', '));
    }, [blacklist]);

    return (
        <Menu tw="w-[360px]">
            <Menu.ColumnSelect
                title="Cloud By"
                onChangeColumn={onChangeWordCloudColumn}
                selectableColumns={placeableColumns}
                selected={wordCloudBy}
            />
            <Menu.Subtitle>Compare By</Menu.Subtitle>
            <Menu.ColumnSelect
                onChangeColumn={onChangeWordCloudCompareColumn}
                selectableColumns={placeableColumns}
                selected={wordCloudCompareBy}
            />
            <Menu.Subtitle>Operation</Menu.Subtitle>
            <Menu.Item tw="mb-3">
                <Select<BoolOpeartion>
                    defaultValue="difference"
                    value={boolOperation}
                    onChange={onChangeBoolOperation}
                    options={[
                        'difference',
                        'intersection',
                        'union',
                        'symmetric difference',
                    ]}
                />
            </Menu.Item>
            <Menu.Title>Scaling</Menu.Title>
            <Menu.Item>
                <Select
                    value={scaling}
                    onChange={onChangeScaling}
                    options={['linear', 'log', 'sqrt']}
                />
            </Menu.Item>
            <Menu.Item>
                <Menu.Title>Word Count</Menu.Title>
                <LabeledSlider
                    showTooltip={true}
                    min={minWordCount}
                    max={maxWordCount}
                    onRelease={onChangeWordCount}
                    value={wordCount}
                />
            </Menu.Item>
            <Menu.Title>Blacklist</Menu.Title>
            <Menu.Item tw="flex">
                <Menu.TextArea
                    placeholder="Blacklist"
                    tw="flex-grow"
                    value={blacklistInputValue}
                    onChange={(event) => setBlacklistInputValue(event.target.value)}
                    onBlur={onChangeBlacklistInput}
                />
            </Menu.Item>
            <Menu.Item>
                <Menu.Title>Min Word Length</Menu.Title>
                <LabeledSlider
                    showTooltip={true}
                    min={1}
                    max={maxWordLength}
                    onRelease={onChangeMinWordLength}
                    value={minWordLength}
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

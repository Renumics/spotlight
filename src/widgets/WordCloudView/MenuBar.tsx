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
    stopwords: string[];
    onChangeStopwords: (values: string[]) => void;
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
    onChangeStopwords,
    stopwords,
    boolOperation,
    onChangeBoolOperation,
    minWordLength,
    maxWordLength,
    onChangeMinWordLength,
}: Omit<Props, 'onChangeFilter' | 'filter'>): JSX.Element => {
    const [stopwordsInputValue, setStopwordsInputValue] = useState(
        stopwords.join(', ')
    );
    const onChangeBlacklistInput = useCallback(() => {
        const newList = stopwordsInputValue.split(/[\s,;]+/);
        if (!_.isEqual(newList, stopwords)) {
            onChangeStopwords(newList);
        }
    }, [stopwords, stopwordsInputValue, onChangeStopwords]);

    useEffect(() => {
        setStopwordsInputValue(stopwords.join(', '));
    }, [stopwords]);

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
            <Menu.Title title="Scaling of the words relative to their count.">
                Scaling
            </Menu.Title>
            <Menu.Item>
                <Select
                    value={scaling}
                    onChange={onChangeScaling}
                    options={['linear', 'log', 'sqrt']}
                />
            </Menu.Item>
            <Menu.Item title="How many of the most common words to take into account.">
                <Menu.Title>Word Count</Menu.Title>
                <LabeledSlider
                    showTooltip={true}
                    min={minWordCount}
                    max={maxWordCount}
                    onRelease={onChangeWordCount}
                    value={wordCount}
                />
            </Menu.Item>
            <Menu.Title title="Words to ignore when computing word cloud.">
                Stopwords
            </Menu.Title>
            <Menu.Item tw="flex">
                <Menu.TextArea
                    placeholder="Blacklist"
                    tw="flex-grow"
                    value={stopwordsInputValue}
                    onChange={(event) => setStopwordsInputValue(event.target.value)}
                    onBlur={onChangeBlacklistInput}
                />
            </Menu.Item>
            <Menu.Item title="Minimum length of a word to be considered for the word cloud.">
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

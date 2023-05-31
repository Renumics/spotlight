import { FunctionComponent, MouseEvent, useCallback, useMemo, useState } from 'react';
import { BsToggleOff as ToggleOff, BsToggleOn as ToggleOn } from 'react-icons/bs';
import tw, { styled } from 'twin.macro';
import { Dataset, useDataset } from '../../stores/dataset';
import { Filter } from '../../types';
import CancelIcon from '../../icons/X';
import Button from './Button';
import FilterEditor from './FilterEditor';
import FilterText from './FilterText';

export interface Props {
    filter: Filter;
}

const SwitchButton = styled(Button)`
    svg {
        width: 1.1rem;
    }
`;

const replaceFilterSelector = (d: Dataset) => d.replaceFilter;
const removeFilterSelector = (d: Dataset) => d.removeFilter;
const toggleFilterEnabledSelector = (d: Dataset) => d.toggleFilterEnabled;
const dataSelector = (d: Dataset) => d.columnData;
const setHighlightedRowsSelector = (d: Dataset) => d.setHighlightedRows;
const dehighlightAllSelector = (d: Dataset) => d.dehighlightAll;
const rowCountSelector = (d: Dataset) => d.length;

const FilterItem: FunctionComponent<Props> = ({ filter }) => {
    const [inEditMode, setInEditMode] = useState(false);

    const replaceFilter = useDataset(replaceFilterSelector);
    const removeFilter = useDataset(removeFilterSelector);
    const toggleFilterEnabled = useDataset(toggleFilterEnabledSelector);
    const data = useDataset(dataSelector);
    const rowCount = useDataset(rowCountSelector);
    const setHighlightedRows = useDataset(setHighlightedRowsSelector);
    const dehighlightAll = useDataset(dehighlightAllSelector);

    const onEdit = useCallback(() => {
        if (!inEditMode) {
            setInEditMode(true);
            dehighlightAll();
        }
    }, [dehighlightAll, inEditMode]);

    const onCancel = () => {
        setInEditMode(false);
    };
    const onAccept = (newFilter: Filter) => {
        setInEditMode(false);
        replaceFilter(filter, newFilter);
    };
    const onRemove = useCallback(
        (e: MouseEvent) => {
            e.stopPropagation();
            removeFilter(filter);
            dehighlightAll();
        },
        [dehighlightAll, removeFilter, filter]
    );
    const onToggleEnabled = useCallback(
        (e: MouseEvent) => {
            e.stopPropagation();
            toggleFilterEnabled(filter);
        },
        [filter, toggleFilterEnabled]
    );

    const highlightMask = useMemo(() => {
        const mask = [];
        for (let i = 0; i < rowCount; i++) {
            mask[i] = filter.apply(i, data);
        }
        return mask;
    }, [filter, data, rowCount]);

    const handleMouseEnter = useCallback(() => {
        if (!inEditMode) {
            setHighlightedRows(highlightMask);
        }
    }, [setHighlightedRows, highlightMask, inEditMode]);
    const handleMouseLeave = useCallback(() => {
        dehighlightAll();
    }, [dehighlightAll]);

    return (
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events,jsx-a11y/no-static-element-interactions
        <div
            onClick={onEdit}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            css={[
                tw`rounded transition-all`,
                !filter.isEnabled && tw`bg-gray-200 text-gray-800`,
            ]}
        >
            {inEditMode ? (
                <FilterEditor filter={filter} onAccept={onAccept} onCancel={onCancel} />
            ) : (
                <div tw="flex flex-row items-center cursor-pointer">
                    <FilterText filter={filter} />
                    <SwitchButton
                        onClick={onToggleEnabled}
                        css={[!filter.isEnabled && tw`text-gray-600`]}
                        tooltip={`${filter.isEnabled ? 'Disable' : 'Enable'} filter`}
                    >
                        {filter.isEnabled ? <ToggleOn /> : <ToggleOff />}
                    </SwitchButton>
                    <Button
                        onClick={onRemove}
                        css={[!filter.isEnabled && tw`text-gray-600`]}
                        tooltip="Delete filter"
                    >
                        <CancelIcon />
                    </Button>
                </div>
            )}
        </div>
    );
};

export default FilterItem;

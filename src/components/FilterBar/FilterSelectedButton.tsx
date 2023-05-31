import GroupSelectionIcon from '../../icons/GroupSelection';
import Button from '../ui/Button';
import { FunctionComponent, useCallback } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import 'twin.macro';
import { SetFilter } from '../../types';
import { shallow } from 'zustand/shallow';

const addFilterSelector = (d: Dataset) => d.addFilter;

const isAnythingSelected = (d: Dataset) =>
    d.isIndexSelected.some((isSelected) => isSelected);

const FilterSelectedButton: FunctionComponent = () => {
    const addFilter = useDataset(addFilterSelector, shallow);

    const anythingSelected = useDataset(isAnythingSelected);

    const handleClickCreateFilter = useCallback(() => {
        // only create a filter if something has been selected
        const isIndexSelected = useDataset.getState().isIndexSelected;
        addFilter(SetFilter.fromMask(isIndexSelected));
    }, [addFilter]);

    const disabled = !anythingSelected;
    const tooltip = disabled
        ? 'Select a subset in order to create a filter from it'
        : 'Create filter from selected rows';

    return (
        <Button onClick={handleClickCreateFilter} disabled={disabled} tooltip={tooltip}>
            +<GroupSelectionIcon />
        </Button>
    );
};

export default FilterSelectedButton;

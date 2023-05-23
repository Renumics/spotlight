import { FunctionComponent } from 'react';
import 'twin.macro';
import { shallow } from 'zustand/shallow';
import { Dataset, useDataset } from '../../stores/dataset';
import { SetFilter } from '../../types';
import UnionIcon from '../../icons/Union';
import Button from './Button';

const dataSelector = (d: Dataset) => ({
    isIndexFiltered: d.isIndexFiltered,
    addFilter: d.addFilter,
    filterCount: d.filters.length,
});

const MergeFiltersButton: FunctionComponent = () => {
    const { isIndexFiltered, addFilter, filterCount } = useDataset(
        dataSelector,
        shallow
    );

    const handleClickCreateFilter = () => {
        // only create a filter if something has been selected
        addFilter(SetFilter.fromMask(isIndexFiltered));
    };

    return (
        <Button
            onClick={handleClickCreateFilter}
            tooltip={'Create new filter from the currently filtered rows'}
            disabled={filterCount === 0}
        >
            +<UnionIcon />
        </Button>
    );
};

export default MergeFiltersButton;

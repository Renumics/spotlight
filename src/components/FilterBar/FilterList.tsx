import { FunctionComponent } from 'react';
import tw from 'twin.macro';
import { useDataset } from '../../stores/dataset';
import FilterCreator from './FilterCreator';
import FilterItem from './FilterItem';
import FilterSelectedButton from './FilterSelectedButton';
import MergeFiltersButton from './MergeFiltersButton';

const Li = tw.li`border border-gray-400 rounded mx-0.5 bg-gray-100`;

const FilterList: FunctionComponent = () => {
    const filters = useDataset((state) => state.filters);

    return (
        <ul tw="flex flex-wrap w-full">
            <>
                {filters.map((filter, index) => (
                    <Li key={index}>
                        <FilterItem filter={filter} />
                    </Li>
                ))}
                <Li>
                    <FilterCreator />
                </Li>
                <Li>
                    <MergeFiltersButton />
                </Li>
                <Li>
                    <FilterSelectedButton />
                </Li>
            </>
        </ul>
    );
};

export default FilterList;

import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';
import dataformat from '../../dataformat';
import { Filter, PredicateFilter, SetFilter } from '../../types';
import SelectionIcon from '../../icons/Selection';

export interface Props {
    filter: Filter;
    className?: string;
}

const FilterIconSpan = styled.span`
    ${tw`mr-1`}
    svg {
        ${tw`w-4! h-4!`}
    }
`;

const PredicateFilterText: FunctionComponent<{ filter: PredicateFilter }> = ({
    filter,
}) => (
    <>
        {filter.column.name} {filter.predicate.shorthand}{' '}
        {dataformat.format(filter.referenceValue, filter.type)}
    </>
);

const SetFilterText: FunctionComponent<{ filter: SetFilter }> = ({ filter }) => (
    <>
        <FilterIconSpan tw="text-sm!">
            <SelectionIcon />
        </FilterIconSpan>
        {filter.name}
    </>
);

const FilterText: FunctionComponent<Props> = ({ filter, className }) => {
    return (
        <div className={className} tw="inline-block px-1">
            {filter.kind === 'PredicateFilter' ? (
                <PredicateFilterText filter={filter as PredicateFilter} />
            ) : (
                filter.kind === 'SetFilter' && (
                    <SetFilterText filter={filter as SetFilter} />
                )
            )}
        </div>
    );
};

export default FilterText;

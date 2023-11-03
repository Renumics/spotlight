import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';
import FilterList from './FilterList';
import { CellDragData, ColumnDragData, Droppable } from '../../systems/dnd';
import {
    PredicateFilter,
    getApplicablePredicates,
    getNullValue,
    useDataset,
} from '../../lib';

const StyledDiv = styled.div`
    ${tw`px-0 py-0 text-midnight-600 py-0.5 z-10 inline-block text-sm`}

    svg {
        ${tw`w-4 h-4 font-semibold inline-block`}
    }

    ul {
        ${tw`flex flex-wrap w-full`}
    }
`;

const Filters: FunctionComponent = () => {
    const handleDrop = (data: ColumnDragData | CellDragData) => {
        const applicablePredicates = getApplicablePredicates(data.column.type.kind);
        const predicate =
            applicablePredicates['unequal'] ?? Object.values(applicablePredicates)[0];
        const referenceValue =
            data.kind === 'column'
                ? getNullValue(data.column.type.kind)
                : useDataset.getState().columnData[data.column.key][data.row];

        if (predicate) {
            useDataset
                .getState()
                .addFilter(new PredicateFilter(data.column, predicate, referenceValue));
        }
    };

    return (
        <Droppable onDrop={handleDrop} tw="flex-grow">
            <StyledDiv data-tour="filterBar">
                <FilterList />
            </StyledDiv>
        </Droppable>
    );
};

export default Filters;

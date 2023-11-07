import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';
import FilterList from './FilterList';
import { CellDragData, ColumnDragData, DragData, Droppable } from '../../systems/dnd';
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
            applicablePredicates[data.kind === 'cell' ? 'equal' : 'unequal'] ??
            Object.values(applicablePredicates)[0];

        const referenceValue =
            data.kind === 'cell'
                ? useDataset.getState().columnData[data.column.key][data.row]
                : getNullValue(data.column.type.kind);

        if (predicate) {
            useDataset
                .getState()
                .addFilter(new PredicateFilter(data.column, predicate, referenceValue));
        }
    };

    const accepts = (data: DragData) => {
        if (!['column', 'cell'].includes(data.kind)) return false;
        return Object.values(getApplicablePredicates(data.column.type.kind)).length > 0;
    };

    return (
        <Droppable accepts={accepts} onDrop={handleDrop} tw="flex-grow">
            <StyledDiv data-tour="filterBar">
                <FilterList />
            </StyledDiv>
        </Droppable>
    );
};

export default Filters;

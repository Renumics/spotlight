import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';
import FilterList from './FilterList';

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
    return (
        <StyledDiv data-tour="filterBar">
            <FilterList />
        </StyledDiv>
    );
};

export default Filters;

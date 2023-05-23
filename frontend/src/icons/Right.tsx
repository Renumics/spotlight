import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';

const StyledSvg = styled.svg`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;

const RightIcon: FunctionComponent = () => {
    return (
        <StyledSvg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </StyledSvg>
    );
};

export default RightIcon;

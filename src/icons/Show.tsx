import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';

const StyledSvg = styled.svg`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;

const ShowIcon: FunctionComponent = () => {
    return (
        <StyledSvg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
            <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
            />
        </StyledSvg>
    );
};

export default ShowIcon;

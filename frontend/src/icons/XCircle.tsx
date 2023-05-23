import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';

const StyledSvg = styled.svg`
    ${tw`w-4 h-4 font-semibold inline-block`}
`;

const XCircleIcon: FunctionComponent = () => {
    return (
        <StyledSvg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
        >
            <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
        </StyledSvg>
    );
};

export default XCircleIcon;

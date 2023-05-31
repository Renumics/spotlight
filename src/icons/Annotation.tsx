import { FunctionComponent } from 'react';
import tw, { styled } from 'twin.macro';

const StyledSvg = styled.svg`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;

const AnnotationIcon: FunctionComponent = () => {
    return (
        <StyledSvg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
            />
        </StyledSvg>
    );
};

export default AnnotationIcon;

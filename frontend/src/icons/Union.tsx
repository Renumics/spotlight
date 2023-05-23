import { FunctionComponent } from 'react';
import tw from 'twin.macro';

const StyledSvg = tw.svg`w-4 h-4 font-semibold inline-block align-middle stroke-current`;

const Union: FunctionComponent = () => {
    return (
        <StyledSvg viewBox="-1 -1 27 27">
            <g fill="none" strokeLinecap="round" strokeLinejoin="round">
                <path
                    d="M10.176 16.145a7.169 7.353 0 014.747-7.852"
                    strokeWidth="1"
                    strokeDasharray="1.779 1.779"
                    strokeDashoffset=".83"
                />
                <path
                    d="M14.833 8.326a7.172 7.172 0 017.92 2.196 7.172 7.172 0 01.658 8.192 7.172 7.172 0 01-7.468 3.432 7.172 7.172 0 01-5.788-5.834"
                    strokeWidth="2"
                />
                <path
                    d="M9.866 16.355a7.172 7.172 0 01-7.786-2.471 7.172 7.172 0 01-.423-8.158 7.172 7.172 0 017.489-3.263 7.172 7.172 0 015.687 5.863"
                    strokeWidth="2"
                />
            </g>
        </StyledSvg>
    );
};

export default Union;

import { FunctionComponent } from 'react';
import tw from 'twin.macro';

const StyledSvg = tw.svg`w-4 h-4 stroke-current stroke-2`;

const DownIcon: FunctionComponent = () => {
    return (
        <StyledSvg fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="8" r="2" />
            <circle cx="17" cy="14" r="2" />
            <circle cx="9" cy="17" r="2" />
            <circle cx="12" cy="12" strokeDasharray="4" r="11" />
        </StyledSvg>
    );
};

export default DownIcon;

import MaximizeIcon from '../../icons/Maximize';
import MinimizeIcon from '../../icons/Minimize';
import tw, { styled } from 'twin.macro';

const StyledMaximizeIcon = styled(MaximizeIcon)`
    ${tw`h-4 w-4 block hover:text-blue-600 active:hover:text-blue-200 text-navy-600 transition-colors`}
`;
const StyledMinimizeIcon = styled(MinimizeIcon)`
    ${tw`h-4 w-4 block hover:text-blue-600 active:hover:text-blue-200 text-navy-600 transition-colors`}
`;

const icons = {
    maximize: <StyledMaximizeIcon />,
    restore: <StyledMinimizeIcon />,
};

export default icons;

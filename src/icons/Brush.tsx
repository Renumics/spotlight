import type { IconType } from 'react-icons';
import { BiBrush as Brush } from 'react-icons/bi';
import tw, { styled } from 'twin.macro';

const StyledBrush: IconType = styled(Brush)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current fill-current`}
    & * {
        ${tw`stroke-0`}
    }
`;

export default StyledBrush;

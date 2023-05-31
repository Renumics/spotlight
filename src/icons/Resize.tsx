import type { IconType } from 'react-icons';
import { HiOutlineSelector as Resize } from 'react-icons/hi';
import tw, { styled } from 'twin.macro';

const StyledResize: IconType = styled(Resize)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;

export default StyledResize;

import type { IconType } from 'react-icons';
import { MdDeleteOutline as Delete } from 'react-icons/md';
import tw, { styled } from 'twin.macro';

const StyledDelete: IconType = styled(Delete)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
`;

export default StyledDelete;

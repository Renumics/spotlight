import type { IconType } from 'react-icons';
import { HiOutlineTable as Table } from 'react-icons/hi';
import tw, { styled } from 'twin.macro';

const StyledTable: IconType = styled(Table)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;

export default StyledTable;

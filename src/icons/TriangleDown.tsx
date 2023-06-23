import type { IconType } from 'react-icons';
import { VscTriangleDown } from 'react-icons/vsc';
import tw, { styled } from 'twin.macro';

const TriangleDown: IconType = styled(VscTriangleDown)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
`;
export default TriangleDown;

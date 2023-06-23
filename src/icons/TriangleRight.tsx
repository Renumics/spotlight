import type { IconType } from 'react-icons';
import { VscTriangleRight } from 'react-icons/vsc';
import tw, { styled } from 'twin.macro';

const TriangleRight: IconType = styled(VscTriangleRight)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
`;
export default TriangleRight;

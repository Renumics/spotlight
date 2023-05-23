import { HiOutlineCube as Cube } from 'react-icons/hi';
import tw, { styled } from 'twin.macro';

const StyledCube = styled(Cube)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
`;

export default StyledCube;

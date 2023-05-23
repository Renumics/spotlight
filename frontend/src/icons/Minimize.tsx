import type { IconType } from 'react-icons';
import { FiMinimize } from 'react-icons/fi';
import tw, { styled } from 'twin.macro';

const Minimize: IconType = styled(FiMinimize)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;
export default Minimize;

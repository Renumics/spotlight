import type { IconType } from 'react-icons';
import { FiMaximize as Maximize } from 'react-icons/fi';
import tw, { styled } from 'twin.macro';

const MaximizeIcon: IconType = styled(Maximize)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;
export default MaximizeIcon;

import type { IconType } from 'react-icons';
import { HiOutlineLocationMarker as Location } from 'react-icons/hi';
import tw, { styled } from 'twin.macro';

const StyledLocation: IconType = styled(Location)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
    & * {
        ${tw`stroke-2`}
    }
`;

export default StyledLocation;

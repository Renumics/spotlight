import type { IconType } from 'react-icons';
import { HiLightBulb as Lightbulb } from 'react-icons/hi';
import tw, { styled } from 'twin.macro';

const StyledLightbulb: IconType = styled(Lightbulb)`
    ${tw`w-4 h-4 font-semibold inline-block align-middle stroke-current`}
`;

export default StyledLightbulb;

import type { IconType } from 'react-icons';
import { IoWarning } from 'react-icons/io5';
import tw from 'twin.macro';

const Warning: IconType = tw(
    IoWarning
)`w-4 h-4 inline-block align-middle stroke-current`;
export default Warning;

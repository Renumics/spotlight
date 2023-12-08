import type { IconType } from 'react-icons';
import { PiBoundingBox } from 'react-icons/pi';
import tw from 'twin.macro';

const BoundingBox: IconType = tw(
    PiBoundingBox
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default BoundingBox;

import type { IconType } from 'react-icons';
import { BsSoundwave } from 'react-icons/bs';
import tw from 'twin.macro';

const Soundwave: IconType = tw(
    BsSoundwave
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Soundwave;

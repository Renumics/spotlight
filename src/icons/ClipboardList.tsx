import type { IconType } from 'react-icons';
import { HiOutlineClipboardList } from 'react-icons/hi';
import tw from 'twin.macro';

const ClipboardList: IconType = tw(
    HiOutlineClipboardList
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default ClipboardList;

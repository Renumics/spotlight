import type { IconType } from 'react-icons';
import { HiOutlineViewGridAdd } from 'react-icons/hi';
import tw from 'twin.macro';

const AddCell: IconType = tw(
    HiOutlineViewGridAdd
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default AddCell;

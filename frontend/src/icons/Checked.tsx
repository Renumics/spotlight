import type { IconType } from 'react-icons';
import { ImCheckboxChecked } from 'react-icons/im';
import tw from 'twin.macro';

const CheckedIcon: IconType = tw(
    ImCheckboxChecked
)`w-4 h-4 max-w-full max-h-full font-semibold inline-block`;

export default CheckedIcon;

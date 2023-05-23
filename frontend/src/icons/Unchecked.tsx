import type { IconType } from 'react-icons';
import { ImCheckboxUnchecked } from 'react-icons/im';
import tw from 'twin.macro';

const UncheckedIcon: IconType = tw(
    ImCheckboxUnchecked
)`w-4 h-4 max-w-full max-h-full font-semibold inline-block`;

export default UncheckedIcon;

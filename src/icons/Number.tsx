import type { IconType } from 'react-icons';
import { VscSymbolNumeric } from 'react-icons/vsc';
import tw from 'twin.macro';

const Number: IconType = tw(
    VscSymbolNumeric
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Number;

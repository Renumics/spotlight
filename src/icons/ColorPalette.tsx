import type { IconType } from 'react-icons';
import { VscSymbolColor } from 'react-icons/vsc';
import tw from 'twin.macro';

const ColorPalette: IconType = tw(VscSymbolColor)`
    w-4 h-4 font-semibold inline-block align-middle stroke-current
`;

export default ColorPalette;

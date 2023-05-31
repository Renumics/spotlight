import type { IconType } from 'react-icons';
import { VscSymbolKey } from 'react-icons/vsc';
import tw from 'twin.macro';

const Text: IconType = tw(
    VscSymbolKey
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Text;

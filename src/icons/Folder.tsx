import type { IconType } from 'react-icons';
import { VscFolder } from 'react-icons/vsc';
import tw from 'twin.macro';

const Folder: IconType = tw(
    VscFolder
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Folder;

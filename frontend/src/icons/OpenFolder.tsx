import type { IconType } from 'react-icons';
import { VscFolderOpened } from 'react-icons/vsc';
import tw from 'twin.macro';

const OpenFolder: IconType = tw(
    VscFolderOpened
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default OpenFolder;

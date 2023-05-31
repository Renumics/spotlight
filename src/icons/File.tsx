import type { IconType } from 'react-icons';
import { VscFile } from 'react-icons/vsc';
import tw from 'twin.macro';

const File: IconType = tw(
    VscFile
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default File;

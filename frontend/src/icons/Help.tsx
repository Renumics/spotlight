import type { IconType } from 'react-icons';
import { RiQuestionLine } from 'react-icons/ri';
import tw from 'twin.macro';

const Help: IconType = tw(
    RiQuestionLine
)`w-4 h-4 font-bold inline-block align-middle stroke-current`;

export default Help;

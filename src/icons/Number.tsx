import type { IconType } from 'react-icons';
import { GoNumber } from 'react-icons/go';
import tw from 'twin.macro';

const Number: IconType = tw(
    GoNumber
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Number;

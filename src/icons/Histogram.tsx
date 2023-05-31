import type { IconType } from 'react-icons';
import { GiHistogram } from 'react-icons/gi';
import tw from 'twin.macro';

const Histogram: IconType = tw(
    GiHistogram
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Histogram;

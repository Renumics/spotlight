import type { IconType } from 'react-icons';
import { LuGauge } from 'react-icons/lu';
import tw from 'twin.macro';

const Gauge: IconType = tw(
    LuGauge
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Gauge;

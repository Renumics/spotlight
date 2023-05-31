import type { IconType } from 'react-icons';
import { VscCalendar } from 'react-icons/vsc';
import tw from 'twin.macro';

const Calendar: IconType = tw(
    VscCalendar
)`w-4 h-4 font-semibold inline-block align-middle stroke-current`;
export default Calendar;

import type { IconType } from 'react-icons';
import { RiMovieLine } from 'react-icons/ri';
import tw from 'twin.macro';

const Movie: IconType = tw(
    RiMovieLine
)`w-4 h-4 inline-block align-middle stroke-current`;
export default Movie;

import type { IconType } from 'react-icons';
import { VscGithubInverted } from 'react-icons/vsc';
import tw from 'twin.macro';

const Github: IconType = tw(
    VscGithubInverted
)`w-4 h-4 font-bold inline-block align-middle stroke-current`;

export default Github;

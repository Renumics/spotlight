import tw from 'twin.macro';

const Svg = tw.svg`text-blue-400 w-full h-full animate-spin rounded-full`;
const Circle = tw.circle`opacity-50 stroke-current`;
const Path = tw.path`text-blue-600 stroke-current`;

interface Props {
    className?: string;
}

const Spinner = ({ className = '' }: Props): JSX.Element => {
    return (
        <Svg
            className={className}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 26 26"
        >
            <Circle cx="13" cy="13" r="10" strokeWidth="4" />
            <Path
                fill="none"
                strokeWidth="4"
                strokeLinecap="round"
                d="M 13 3 A 10 10 0 0 1 23 13"
            />
        </Svg>
    );
};

export default Spinner;

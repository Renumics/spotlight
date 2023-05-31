import chroma, { Color } from 'chroma-js';
import { theme } from 'twin.macro';

interface Props {
    tag: string;
    color?: Color;
    className?: string;
}

const Tag = ({
    tag,
    color = chroma(theme`colors.gray.200`),
    className,
}: Props): JSX.Element => {
    const white = chroma(theme`colors.white`);
    const black = chroma(theme`colors.black`);

    const textColor =
        chroma.contrast(color, white) > chroma.contrast(color, black) ? white : black;

    return (
        <div
            className={className}
            tw="m-0.5 px-1 rounded text-xs text-midnight-600/80 overflow-ellipsis truncate w-auto"
            style={{ backgroundColor: color?.css(), color: textColor.css() }}
        >
            {tag}
        </div>
    );
};

export default Tag;

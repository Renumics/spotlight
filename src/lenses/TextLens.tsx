import 'twin.macro';
import { Lens } from '../types';

const TextLens: Lens<string> = ({ value }) => {
    return (
        <div tw="w-full h-full overflow-y-auto p-1 text-xs whitespace-pre-wrap">
            {value}
        </div>
    );
};

TextLens.key = 'TextLens';
TextLens.dataTypes = ['str'];
TextLens.defaultHeight = 48;
TextLens.minHeight = 22;
TextLens.maxHeight = 512;
TextLens.displayName = 'Text';

export default TextLens;

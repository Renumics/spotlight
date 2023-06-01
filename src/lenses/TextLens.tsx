import 'twin.macro';
import { Lens } from './types';

const TextLens: Lens = ({ value }) => {
    return <div>{value as string}</div>;
};

TextLens.dataTypes = ['str'];
TextLens.defaultHeight = 48;
TextLens.minHeight = 22;
TextLens.maxHeight = 512;
TextLens.displayName = 'Text';

export default TextLens;

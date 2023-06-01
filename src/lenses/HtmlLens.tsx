import 'twin.macro';
import Html from '../components/ui/Html';
import { Lens } from './types';

const HtmlLens: Lens = ({ value }) => {
    return <Html html={value as string} />;
};

HtmlLens.dataTypes = ['str'];
HtmlLens.defaultHeight = 48;
HtmlLens.minHeight = 22;
HtmlLens.maxHeight = 512;
HtmlLens.displayName = 'HTML (unsafe)';

export default HtmlLens;

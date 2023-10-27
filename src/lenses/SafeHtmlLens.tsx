import 'twin.macro';
import { Lens } from '../types';
import DOMPurify from 'dompurify';
import Html from '../components/ui/Html';

const SafeHtmlLens: Lens<string> = ({ value }) => {
    const safe_html = DOMPurify.sanitize(value);

    return <Html html={safe_html} />;
};

SafeHtmlLens.key = 'SafeHtmlLens';
SafeHtmlLens.dataTypes = ['str'];
SafeHtmlLens.defaultHeight = 48;
SafeHtmlLens.minHeight = 22;
SafeHtmlLens.maxHeight = 512;
SafeHtmlLens.displayName = 'HTML';

export default SafeHtmlLens;

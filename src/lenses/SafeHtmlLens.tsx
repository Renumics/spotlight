import 'twin.macro';
import { Lens } from './types';
import DOMPurify from 'dompurify';

const SafeHtmlLens: Lens = ({ value }) => {
    const unsafe_html = value as string;
    const safe_html = DOMPurify.sanitize(unsafe_html);

    return (
        <div
            tw="text-xs content-center items-center h-full w-full"
            dangerouslySetInnerHTML={{ __html: safe_html }}
        />
    );
};

SafeHtmlLens.dataTypes = ['str'];
SafeHtmlLens.defaultHeight = 48;
SafeHtmlLens.minHeight = 22;
SafeHtmlLens.maxHeight = 512;
SafeHtmlLens.displayName = 'HTML';

export default SafeHtmlLens;

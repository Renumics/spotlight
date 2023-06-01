import 'twin.macro';
import { Lens } from './types';

const HtmlLens: Lens = ({ value }) => {
    const html = value as string;

    return (
        <div
            tw="text-xs content-center items-center h-full w-full"
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
};

HtmlLens.dataTypes = ['str'];
HtmlLens.defaultHeight = 48;
HtmlLens.minHeight = 22;
HtmlLens.maxHeight = 512;
HtmlLens.displayName = 'HTML (unsafe)';

export default HtmlLens;

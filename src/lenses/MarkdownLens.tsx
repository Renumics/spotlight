import showdown from 'showdown';
import { useMemo } from 'react';

import { Lens } from '../types';
import Html from '../components/ui/Html';

const MarkdownLens: Lens = ({ value }) => {
    const markdown = value as string;
    const html = useMemo(() => {
        return new showdown.Converter().makeHtml(markdown);
    }, [markdown]);

    return <Html html={html} />;
};

MarkdownLens.key = 'MarkdownLens';
MarkdownLens.dataTypes = ['str'];
MarkdownLens.defaultHeight = 128;
MarkdownLens.minHeight = 22;
MarkdownLens.displayName = 'Markdown';

export default MarkdownLens;

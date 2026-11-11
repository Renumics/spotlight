import showdown from 'showdown';
import DOMPurify from 'dompurify';
import { useMemo } from 'react';

import Html from './Html';

interface Props {
    content: string;
}

const Markdown = ({ content }: Props): JSX.Element => {
    const html = useMemo(() => {
        return DOMPurify.sanitize(new showdown.Converter().makeHtml(content));
    }, [content]);
    return <Html html={html} />;
};

export default Markdown;

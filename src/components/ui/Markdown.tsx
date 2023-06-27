import showdown from 'showdown';
import { useMemo } from 'react';

import Html from './Html';

interface Props {
    content: string;
}

const Markdown = ({ content }: Props): JSX.Element => {
    const html = useMemo(() => {
        return new showdown.Converter().makeHtml(content);
    }, [content]);
    return <Html html={html} />;
};

export default Markdown;

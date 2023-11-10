import { Lens } from '../types';
import Markdown from '../components/ui/Markdown';

const MarkdownLens: Lens = ({ value }) => {
    return <Markdown content={value as string} />;
};

MarkdownLens.kind = 'MarkdownLens';
MarkdownLens.dataTypes = ['str'];
MarkdownLens.defaultHeight = 128;
MarkdownLens.minHeight = 22;
MarkdownLens.displayName = 'Markdown';

export default MarkdownLens;

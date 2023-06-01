import { DataType } from '../datatypes';
import { Lens } from './types';
import AudioLens from './AudioLens';
import ImageLens from './ImageLens';
import MeshLens from './MeshLens';
import ScalarLens from './ScalarLens';
import ArrayLens from './ArrayLens';
import SequenceLens from './SequenceLens';
import SpectrogramLens from './SpectrogramLens';
import VideoLens from './VideoLens';
import HtmlLens from './HtmlLens';
import SafeHtmlLens from './SafeHtmlLens';
import MarkdownLens from './MarkdownLens';
import TextLens from './TextLens';

export type LensKey = string;
interface Registry {
    views: Record<LensKey, Lens>;
    keys: string[];
    findCompatibleViews(types: DataType[], canEdit: boolean): string[];
    register(lens: Lens): void;
}

export function isLensCompatible(
    view: Lens,
    types: DataType[],
    canEdit: boolean
): boolean {
    return !!(
        types.length &&
        (canEdit || !view.isEditor) &&
        (types.length === 1 || view.multi) &&
        types.every((t) => view.dataTypes.includes(t.kind))
    );
}

const registry: Registry = {
    views: {
        AudioView: AudioLens,
        SpectrogramView: SpectrogramLens,
        VideoView: VideoLens,
        ImageView: ImageLens,
        MeshView: MeshLens,
        ScalarView: ScalarLens,
        SequenceView: SequenceLens,
        ArrayLens,
        SafeHtmlLens,
        HtmlLens,
        MarkdownLens,
        TextLens,
    },
    get keys() {
        return Object.keys(this.views);
    },
    findCompatibleViews(types, canEdit) {
        return Object.keys(this.views).filter((viewName) =>
            isLensCompatible(this.views[viewName], types, canEdit)
        );
    },
    register(lens) {
        const lensKey = lens.key ?? lens.displayName;
        this.views[lensKey] = lens;
    },
} as const;
export default registry;

import { DataType } from '../datatypes';
import { Lens } from '../types';
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

type LensKey = string;
interface Registry {
    _views: Record<LensKey, Lens>;
    _keys: string[];
    _findCompatibleViews(types: DataType[], canEdit: boolean): string[];
    _register(lens: Lens): void;
}

function isLensCompatible(view: Lens, types: DataType[], canEdit: boolean): boolean {
    return !!(
        types.length &&
        (canEdit || !view.isEditor) &&
        (types.length === 1 || view.multi) &&
        types.every((t) => view.dataTypes.includes(t.kind))
    );
}

const registry: Registry = {
    _views: {
        AudioView: AudioLens,
        SpectrogramView: SpectrogramLens,
        VideoView: VideoLens,
        ImageView: ImageLens,
        MeshView: MeshLens,
        SequenceView: SequenceLens,
        TextLens,
        ArrayLens,
        SafeHtmlLens,
        HtmlLens,
        MarkdownLens,
        ScalarView: ScalarLens,
    },
    get _keys() {
        return Object.keys(this._views);
    },
    _findCompatibleViews(types, canEdit) {
        return Object.keys(this._views).filter((viewName) =>
            isLensCompatible(this._views[viewName], types, canEdit)
        );
    },
    _register(lens) {
        const lensKey = lens.key ?? lens.displayName;
        this._views[lensKey] = lens;
    },
} as const;
export default registry;

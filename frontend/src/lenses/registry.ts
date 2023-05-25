import { DataType } from '../datatypes';
import { Lens } from './types';
import AudioView from './AudioView';
import ImageView from './ImageView';
import MeshView from './MeshView';
import ScalarView from './ScalarView';
import SequenceView from './SequenceView';
import SpectrogramView from './SpectrogramView';
import VideoView from './VideoView';

export type ViewKey = string;
interface Registry {
    views: Record<ViewKey, Lens>;
    keys: string[];
    findCompatibleViews(types: DataType[], canEdit: boolean): string[];
    register(lens: Lens): void;
}

export function isViewCompatible(
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
        AudioView,
        SpectrogramView,
        VideoView,
        ImageView,
        MeshView,
        ScalarView,
        SequenceView,
    },
    get keys() {
        return Object.keys(this.views);
    },
    findCompatibleViews(types, canEdit) {
        return Object.keys(this.views).filter((viewName) =>
            isViewCompatible(this.views[viewName], types, canEdit)
        );
    },
    register(lens) {
        const lensKey = lens.key ?? lens.displayName;
        this.views[lensKey] = lens;
    },
} as const;
export default registry;

import { LensKey } from '../../lenses/registry';

export interface ViewConfig {
    view: LensKey;
    key: string;
    name: string;
    columns: string[];
}

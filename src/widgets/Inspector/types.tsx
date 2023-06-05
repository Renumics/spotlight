import { LensKey } from '../../types';

export interface ViewConfig {
    view: LensKey;
    key: string;
    name: string;
    columns: string[];
}

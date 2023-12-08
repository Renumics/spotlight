import { LensKey, LensSettings } from '../../types';

export interface LensConfig {
    view: LensKey;
    key: string;
    name: string;
    columns: string[];
    settings: LensSettings;
}

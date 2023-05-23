import { ViewKey } from '../../lenses/registry';

export interface ViewConfig {
    view: ViewKey;
    key: string;
    name: string;
    columns: string[];
}

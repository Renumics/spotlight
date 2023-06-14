import { useDataset } from '../src/stores/dataset';
export { useColors } from '../src/stores/colors';
import styled from 'styled-components';

export {};

interface Store {
    useDataset: typeof useDataset;
    useColors: typeof useColors;
}

interface Spotlight {
    store: Store;
}

declare global {
    var [styled]: typeof styled;
    var [Spotlight]: Spotlight;
    var [global]: Window;
    var [__filebrowsing_allowed__]: boolean;
}

import { createContext } from 'react';
import { Settings } from './types';

interface State {
    groupKey: string;
    settings: Settings;
    changeSettings: (settings: Settings) => void;
}

const ViewContext = createContext<State>({
    groupKey: '',
    settings: {},
    changeSettings: () => null,
});
export default ViewContext;

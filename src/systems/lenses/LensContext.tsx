import { createContext } from 'react';

interface Setting<T = unknown> {
    value: T;
}

type Settings = Record<string, Setting>;

interface State {
    groupKey: string;
    settings: Record<string, Setting>;
    changeSettings: (settings: Settings) => void;
}

const ViewContext = createContext<State>({
    groupKey: '',
    settings: {},
    changeSettings: () => null,
});
export default ViewContext;

import { createContext } from 'react';

interface State {
    groupKey: string;
}

const ViewContext = createContext<State>({
    groupKey: '',
});
export default ViewContext;

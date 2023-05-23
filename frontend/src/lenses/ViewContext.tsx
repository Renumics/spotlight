import { createContext } from 'react';

interface ViewContextType {
    syncKey: string;
}

const defaultViewContext: ViewContextType = {
    syncKey: '',
};

const ViewContext = createContext(defaultViewContext);
export default ViewContext;

import { createContext } from 'react';
import { LensSettings, Setter } from '../types';

interface LensContextType {
    settings: LensSettings;
    onChangeSettings: Setter<LensSettings>;
}

const defaultLensContext: LensContextType = {
    settings: {},
    onChangeSettings: () => null,
};

const LensContext = createContext(defaultLensContext);
export default LensContext;

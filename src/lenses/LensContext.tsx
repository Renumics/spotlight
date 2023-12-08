import { createContext } from 'react';
import { LensSettings, Setter } from '../types';

interface LensContextType {
    settings: LensSettings;
    onChangeSettings: Setter<LensSettings>;
    sharedState: Record<string, unknown>;
    setSharedState: Setter<Record<string, unknown>>;
}

const defaultLensContext: LensContextType = {
    settings: {},
    onChangeSettings: () => null,
    sharedState: {},
    setSharedState: () => null,
};

const LensContext = createContext(defaultLensContext);
export default LensContext;

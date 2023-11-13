import { useContext, useMemo } from 'react';
import LensContext from './LensContext';
import { Settings } from './types';

function useSettings(defaults: Settings) {
    const { settings } = useContext(LensContext);
    const completeSettings = useMemo(
        () => ({ ...defaults, settings }),
        [defaults, settings]
    );
    return completeSettings;
}
export default useSettings;

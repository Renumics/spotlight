import { createContext, useContext } from 'react';
import { Config } from './types';

interface WidgetContextValue {
    widgetId: string;
    config: Config;
    setConfig: React.Dispatch<React.SetStateAction<Config>>;
}

const defaultWidgetContext: WidgetContextValue = {
    widgetId: 'no widget here',
    config: {},
    setConfig: () => {
        //empty
    },
};

export const WidgetContext = createContext(defaultWidgetContext);
export const useWidgetContext = (): WidgetContextValue => useContext(WidgetContext);

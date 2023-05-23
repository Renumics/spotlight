import { FunctionComponent } from 'react';

export type Config = Record<string, unknown>;

export interface WidgetProps {
    widgetId: string;
}

interface WidgetAttributes {
    defaultName: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    icon: (props?: any) => JSX.Element;
    key: string;
    legacyKeys?: string[];
}

// eslint-disable-next-line @typescript-eslint/ban-types
export type Widget<P = {}> = FunctionComponent<P & WidgetProps> & WidgetAttributes;

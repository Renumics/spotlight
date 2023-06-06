import _ from 'lodash';
import { create } from 'zustand';
import { appBarItems } from '../components/AppBar';
import { Widget } from '../widgets/types';
import { widgets, widgetsById } from '../widgets/WidgetFactory';
import api from '../api';
import { registerLens } from './components';
import { Lens } from '../types';

export interface App {
    registerWidget: (widget: Widget) => void;
    registerLens: (lens: Lens) => void;
    addAppBarItem: (component: JSX.Element) => void;
    removeAppBarItemByKey: (key: string) => void;
}

interface PluginModule {
    activate?: (app: App) => void;
}

interface Plugin {
    name: string;
    priority: number;
    module?: PluginModule;
}

interface State {
    plugins?: Plugin[];
    init: () => void;
}

const usePluginStore = create<State>()((set) => ({
    plugins: undefined,
    init: async () => {
        const apiPlugins = await api.plugin.getPlugins();
        const initializedPlugins: Plugin[] = [];

        for (const pluginInfo of apiPlugins) {
            const plugin: Plugin = {
                name: pluginInfo.name,
                priority: pluginInfo.priority,
            };

            if (pluginInfo.entrypoint) {
                const moduleUrl = pluginInfo.dev
                    ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
                      `${(globalThis as any).__vite__url__}/src/main.tsx`
                    : pluginInfo.entrypoint;

                try {
                    const { default: mod } = await import(moduleUrl /* @vite-ignore */);
                    plugin.module = mod as unknown as PluginModule;
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                } catch (e: any) {
                    console.error(
                        `Failed to import modules for plugin: ${pluginInfo.name}`
                    );
                    console.warn(e.stack);
                    console.warn(e.message);
                }
            }
            initializedPlugins.push(plugin);
        }

        const app: App = {
            registerWidget: (widget: Widget) => {
                _.remove(widgets, (w) => w.key === widget.key);
                widgets.push(widget);
                widgetsById[widget.key] = widget;
            },
            registerLens,
            addAppBarItem: (item: JSX.Element) => {
                appBarItems.push(item);
            },
            removeAppBarItemByKey: (key: string) => {
                const idx = appBarItems.findIndex((x) => x.key === key);
                if (idx !== -1) {
                    appBarItems.splice(idx, 1);
                }
            },
        };

        for (const plugin of initializedPlugins) {
            plugin.module?.activate?.(app);
        }

        set({
            plugins: initializedPlugins,
        });
    },
}));

usePluginStore.getState().init();

export default usePluginStore;

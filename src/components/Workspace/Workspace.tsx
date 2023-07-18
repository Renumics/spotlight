import _ from 'lodash';
import { Widget } from '../../widgets/types';
import {
    Actions,
    BorderNode,
    DockLocation,
    Layout,
    Model,
    TabNode,
    TabSetNode,
} from 'flexlayout-react';
import type { IJsonModel, IJsonRowNode } from 'flexlayout-react';
import type { ITabSetRenderValues } from 'flexlayout-react/declarations/view/Layout';
import {
    forwardRef,
    ForwardRefRenderFunction,
    useCallback,
    useEffect,
    useImperativeHandle,
    useRef,
    useState,
} from 'react';
import guid from 'short-uuid';
import { Dataset, useDataset } from '../../stores/dataset';
import 'twin.macro';
import api from '../../api';
import AddWidgetDropdown from './AddWidgetDropdown';
import ComponentFactory from './ComponentFactory';
import icons from './icons';
import { convertAppLayoutToFlexLayout, convertFlexLayoutToAppLayout } from './layout';
import Styles from './Styles';
import { useLayout } from '../../stores/layout';
import { AppLayout } from '../../types';

const datasetUidSelector = (d: Dataset) => d.uid;
const useDatasetUid = () => useDataset(datasetUidSelector);

const replaceLabels = (label: string, content?: string) => {
    switch (label) {
        case 'Restore tabset':
            return 'Minimize';
        case 'Maximize tabset':
            return 'Maximize';
        case 'Move: ':
            return content ?? undefined;
        default:
            return undefined;
    }
};

export interface Handle {
    reset: () => void;
    loadLayout: (file: File) => void;
    saveLayout: () => void;
}

const GLOBAL_CONFIG = {
    rootOrientationVertical: true,
    splitterSize: 1,
    tabEnableClose: true,
    tabEnableRename: true,
    tabSetHeaderHeight: 24,
    tabSetTabStripHeight: 24,
    tabSetMinHeight: 23,
    tabSetMinWidth: 23,
    tabDragSpeed: 0.2,
};

const Workspace: ForwardRefRenderFunction<Handle> = (_props, ref) => {
    const [model, setModel] = useState<Model>();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const datasetUid = useDatasetUid();

    const layoutStore = useLayout();

    useEffect(() => {
        setIsLoading(true);
        useLayout.getState().fetch();
    }, [datasetUid]);

    useEffect(() => {
        if (!layoutStore.layout) {
            setModel(undefined);
            setIsLoading(false);
            return;
        }
        const layout = convertAppLayoutToFlexLayout(layoutStore.layout);
        const config: IJsonModel = {
            global: GLOBAL_CONFIG,
            layout: layout,
        };
        const model = Model.fromJson(config);
        setModel(model);
        setIsLoading(false);
    }, [layoutStore.layout]);

    useImperativeHandle(
        ref,
        () => ({
            reset: useLayout.getState().reset,
            saveLayout: () => {
                if (!model) return;
                const layout = convertFlexLayoutToAppLayout(model.toJson()['layout']);
                useLayout.getState().save(layout);
            },
            loadLayout: useLayout.getState().load,
        }),
        [model]
    );

    const lastAppLayout = useRef<AppLayout>();
    const handleModelChange = useCallback(() => {
        if (!model) return;

        const flexLayout = model.toJson().layout;
        const appLayout = convertFlexLayoutToAppLayout(flexLayout);

        // only set layout via api if it actually changed
        if (_.isEqual(appLayout, lastAppLayout.current)) return;
        lastAppLayout.current = appLayout;

        api.layout.setLayout({ setLayoutRequest: { layout: appLayout } });
    }, [model]);

    const handleRenderTabSet = useCallback(
        (tabset: TabSetNode | BorderNode, values: ITabSetRenderValues) => {
            if (!model) return;
            const addWidget = (widget: Widget) => {
                const tabNames = new Set();

                model.visitNodes((node) => {
                    if (node.getType() === 'tab') {
                        const tab = node as TabNode;
                        tabNames.add(tab.getName());
                    }
                });

                let modifiedName = widget.defaultName;
                for (let index = 2; tabNames.has(modifiedName); index++) {
                    modifiedName = `${widget.defaultName} (${index})`;
                }

                const addWidget = Actions.addNode(
                    {
                        type: 'tab',
                        component: widget.key,
                        name: modifiedName,
                        id: guid.generate(),
                    },
                    tabset.getId(),
                    DockLocation.CENTER,
                    -1
                );
                model.doAction(addWidget);
            };

            values.stickyButtons = [
                <div
                    key="addWidget"
                    className="flexlayout__tab_button flexlayout__tab_button_top flexlayout__tab_button--unselected"
                    tw="h-full"
                >
                    <AddWidgetDropdown key="addWidget" addWidget={addWidget} />
                </div>,
            ];
        },
        [model]
    );

    if (isLoading || !model) {
        return <></>;
    }

    return (
        <Styles>
            <Layout
                model={model}
                onRenderTabSet={handleRenderTabSet}
                factory={ComponentFactory}
                i18nMapper={replaceLabels}
                icons={icons}
                onModelChange={handleModelChange}
            />
        </Styles>
    );
};

export default forwardRef(Workspace);

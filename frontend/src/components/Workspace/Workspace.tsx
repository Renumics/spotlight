import { Widget } from '../../widgets/types';
import { saveAs } from 'file-saver';
import {
    Actions,
    BorderNode,
    DockLocation,
    Layout,
    Model,
    TabNode,
    TabSetNode,
} from 'flexlayout-react';
import type { IJsonModel } from 'flexlayout-react';
import type { ITabSetRenderValues } from 'flexlayout-react/declarations/view/Layout';
import {
    forwardRef,
    ForwardRefRenderFunction,
    useCallback,
    useEffect,
    useImperativeHandle,
    useState,
} from 'react';
import guid from 'short-uuid';
import { Dataset, useDataset } from '../../stores/dataset';
import 'twin.macro';
import { AppLayout } from '../../types';
import api from '../../api';
import AddWidgetDropdown from './AddWidgetDropdown';
import ComponentFactory from './ComponentFactory';
import icons from './icons';
import { convertAppLayoutToFlexLayout, convertFlexLayoutToAppLayout } from './layout';
import Styles from './Styles';

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

const Workspace: ForwardRefRenderFunction<Handle> = (_, ref) => {
    const [model, setModel] = useState<Model>();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const datasetUid = useDatasetUid();

    useImperativeHandle(
        ref,
        () => ({
            reset: () => {
                api.layout.resetLayout().then((appLayout) => {
                    const layout = convertAppLayoutToFlexLayout(appLayout as AppLayout);
                    const config: IJsonModel = {
                        global: GLOBAL_CONFIG,
                        layout: layout,
                    };
                    const model = Model.fromJson(config);
                    setModel(model);
                });
            },
            saveLayout: () => {
                if (!model) return;
                const layout = convertFlexLayoutToAppLayout(model.toJson()['layout']);
                const blob = new Blob([JSON.stringify(layout)], {
                    type: 'application/json;charset=utf-8',
                });
                saveAs(blob, 'spotlight-layout.json');
            },
            loadLayout: (file: File) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    if (!e.target) return;
                    const parsedLayout = JSON.parse(e.target.result as string);
                    api.layout
                        .setLayout({ setLayoutRequest: { layout: parsedLayout } })
                        .then((appLayout) => {
                            const layout = convertAppLayoutToFlexLayout(
                                appLayout as AppLayout
                            );
                            const config: IJsonModel = {
                                global: GLOBAL_CONFIG,
                                layout: layout,
                            };
                            const model = Model.fromJson(config);
                            setModel(model);
                        });
                };
                reader.readAsText(file);
            },
        }),
        [model]
    );

    useEffect(() => {
        if (!datasetUid) return;
        const loadLayout = async () => {
            setIsLoading(true);

            const response = await api.layout.getLayout();
            const storedLayout = convertAppLayoutToFlexLayout(response as AppLayout);

            const config: IJsonModel = {
                global: GLOBAL_CONFIG,
                layout: storedLayout,
            };
            const model = Model.fromJson(config);

            setModel(model);
            setIsLoading(false);
        };
        loadLayout().catch((e) => console.error(e));
    }, [datasetUid]);

    const handleModelChange = useCallback(() => {
        if (!model) return;

        const flexLayout = model.toJson().layout;
        const appLayout = convertFlexLayoutToAppLayout(flexLayout);
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

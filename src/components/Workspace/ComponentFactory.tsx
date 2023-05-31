import { Config } from '../../widgets/types';
import WidgetFactory from '../../widgets/WidgetFactory';
import { Actions, TabNode } from 'flexlayout-react';
import _ from 'lodash';
import { useCallback } from 'react';

interface Props {
    node: TabNode;
}

const EMPTY_CONFIG = {};

const Component = ({ node }: Props): JSX.Element => {
    const widgetType = node.getComponent();
    const widgetId = node.getId();

    const setConfig: React.Dispatch<React.SetStateAction<Config>> = useCallback(
        (value) => {
            const config = _.isFunction(value)
                ? value(node.getConfig() ?? EMPTY_CONFIG)
                : value;
            node.getModel().doAction(
                Actions.updateNodeAttributes(node.getId(), {
                    config,
                })
            );
        },
        [node]
    );
    const config = node.getConfig() ?? EMPTY_CONFIG;

    if (widgetType) {
        return (
            <WidgetFactory
                widgetType={widgetType}
                widgetId={widgetId}
                config={config}
                setConfig={setConfig}
            />
        );
    } else {
        return <></>;
    }
};

const ComponentFactory = (node: TabNode): JSX.Element => {
    return <Component key={node.getId()} node={node} />;
};

export default ComponentFactory;

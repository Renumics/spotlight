import type { IJsonModel } from 'flexlayout-react';
import type {
    IJsonRowNode,
    IJsonTabNode,
    IJsonTabSetNode,
} from 'flexlayout-react/declarations/model/IJsonModel';
import { useComponentsStore } from '../../stores/components';
import { AppLayout, ContainerNode, SplitNode, TabNode, WidgetNode } from '../../types';

type Orientation = 'horizontal' | 'vertical';

interface ParserState {
    parentOrientation: Orientation;
    tabNames: Set<string>;
}

function flipOrientation(orientation: 'horizontal' | 'vertical') {
    if (orientation === 'horizontal') return 'vertical';
    return 'horizontal';
}

function convertSplitNode(node: SplitNode, state: ParserState): IJsonRowNode {
    const parentOrientation = state.parentOrientation;

    state.parentOrientation = node.orientation ?? flipOrientation(parentOrientation);
    const children = node.children.map((child) => convertContainerNode(child, state));

    if (parentOrientation === state.parentOrientation) {
        return {
            type: 'row',
            weight: node.weight,
            children: [
                {
                    type: 'row',
                    weight: 1,
                    children,
                } as IJsonRowNode,
            ],
        };
    }
    return { type: 'row', weight: node.weight, children };
}

function convertTabNode(node: TabNode, state: ParserState): IJsonTabSetNode {
    const children = node.children.map((child) => convertWidgetNode(child, state));
    return {
        type: 'tabset',
        weight: node.weight,
        selected: 0,
        children,
    };
}

function convertWidgetNode(node: WidgetNode, state: ParserState): IJsonTabNode {
    const widgetsByKey = useComponentsStore.getState().widgetsByKey;
    const name = node.name ?? widgetsByKey[node.type]?.defaultName;
    let modifiedName = name;
    for (let index = 2; state.tabNames.has(modifiedName); index++) {
        modifiedName = `${name} (${index})`;
    }
    state.tabNames.add(modifiedName);
    return {
        name: modifiedName,
        component: node.type,
        config: node.config,
    };
}

function convertContainerNode(
    node: ContainerNode,
    state: ParserState
): IJsonRowNode | IJsonTabSetNode {
    switch (node?.kind) {
        case 'split':
            return convertSplitNode(node, state);
        case 'tab':
            return convertTabNode(node, state);
    }
}

export function convertAppLayoutToFlexLayout(
    appLayout: AppLayout
): IJsonModel['layout'] {
    const orientation = appLayout.orientation ?? 'vertical';

    const tabNames = new Set<string>();

    const children = appLayout.children.map((child) =>
        convertContainerNode(child, { parentOrientation: orientation, tabNames })
    );

    if (orientation === 'horizontal') {
        return {
            type: 'row',
            weight: 1,
            children: [
                {
                    type: 'row',
                    weight: 1,
                    children,
                },
            ],
        };
    } else {
        return {
            type: 'row',
            weight: 1,
            children,
        };
    }
}

function convertFlexWidget(node: IJsonTabNode): WidgetNode {
    return {
        kind: 'widget',
        name: node.name ?? '',
        type: node.component ?? '',
        config: node.config,
    };
}

function convertFlexTabset(node: IJsonTabSetNode): TabNode {
    return {
        kind: 'tab',
        weight: node.weight ?? 1,
        children: node.children.map(convertFlexWidget),
    };
}

function convertFlexContainer(
    node: IJsonRowNode | IJsonTabSetNode,
    parentOrientation: Orientation
): SplitNode | TabNode {
    switch (node.type) {
        case 'row':
            return convertFlexRow(node, parentOrientation);
        case 'tabset':
            return convertFlexTabset(node);
    }
}

export function convertFlexRow(
    node: IJsonRowNode,
    parentOrientation: Orientation
): SplitNode {
    const orientation = flipOrientation(parentOrientation);

    if (node.children.length === 1 && node.children[0].type === 'row') {
        return convertFlexRow(node.children[0], orientation);
    }

    const children = node.children.map((child) =>
        convertFlexContainer(child, orientation)
    );

    return {
        kind: 'split',
        weight: node.weight ?? 1,
        orientation,
        children,
    };
}

export function convertFlexLayoutToAppLayout(
    flexLayout: IJsonModel['layout']
): AppLayout {
    if (flexLayout.type !== 'row') {
        console.error('Invalid root node in flex layout!');
        return { children: [] };
    }

    const node = convertFlexRow(flexLayout as IJsonRowNode, 'horizontal');
    return {
        orientation: node.orientation,
        children: node.children,
    };
}

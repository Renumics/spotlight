export interface BaseLayoutNode {
    kind: string;
}

export interface SplitNode extends BaseLayoutNode {
    kind: 'split';
    weight: number;
    orientation?: 'horizontal' | 'vertical';
    children: ContainerNode[];
}

export interface WidgetNode extends BaseLayoutNode {
    kind: 'widget';
    type: string;
    name?: string;
    config?: Record<string, unknown>;
}

export interface TabNode extends BaseLayoutNode {
    kind: 'tab';
    weight: number;
    children: WidgetNode[];
}

export type ContainerNode = SplitNode | TabNode;
export type LayoutNode = ContainerNode | WidgetNode;

export interface AppLayout {
    orientation?: 'horizontal' | 'vertical';
    children: ContainerNode[];
}

import { PointerActivationConstraints } from '@dnd-kit/dom';
import {
    DragDropProvider,
    DragOverlay,
    KeyboardSensor,
    PointerSensor,
} from '@dnd-kit/react';
import type { DragEndEvent } from '@dnd-kit/react';
import React from 'react';
import 'twin.macro';
import OverlayFactory from './OverlayFactory';
import { DragData, DropData } from './types';

interface Props {
    children: React.ReactNode;
}

// Every table cell is a drag source, so that its value can be dropped on the filter
// bar or a histogram. Cells are clicked far more often than they are dragged, and a
// click must never become a drag. dnd-kit's default also starts a drag when the
// press is held for 200 ms without moving, or after a movement of 5 px, and the
// click that would select the row is lost. Start a mouse drag only after a movement
// of 12 px. A touch drag still needs a long press, so that a touch can scroll.
const sensors = [
    PointerSensor.configure({
        activationConstraints: (event) =>
            event.pointerType === 'touch'
                ? [new PointerActivationConstraints.Delay({ value: 250, tolerance: 5 })]
                : [new PointerActivationConstraints.Distance({ value: 12 })],
    }),
    KeyboardSensor,
];

export default function DragContext({ children }: Props): JSX.Element {
    const handleDragEnd = (event: DragEndEvent) => {
        const { source, target } = event.operation;
        if (event.canceled || !source || !target) return;

        const data = source.data as DragData;
        const dropData = target.data as DropData;
        if (dropData.accepts(data)) {
            dropData.onDrop(data);
        }
    };

    return (
        <DragDropProvider sensors={sensors} onDragEnd={handleDragEnd}>
            {children}
            <DragOverlay style={{ width: 'auto' }} tw="shadow-lg touch-none">
                {(source) => <OverlayFactory data={source.data as DragData} />}
            </DragOverlay>
        </DragDropProvider>
    );
}

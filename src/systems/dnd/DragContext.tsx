import { DragDropProvider, DragOverlay } from '@dnd-kit/react';
import type { DragEndEvent } from '@dnd-kit/react';
import React from 'react';
import 'twin.macro';
import OverlayFactory from './OverlayFactory';
import { DragData, DropData } from './types';

interface Props {
    children: React.ReactNode;
}

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
        <DragDropProvider onDragEnd={handleDragEnd}>
            {children}
            <DragOverlay style={{ width: 'auto' }} tw="shadow-lg touch-none">
                {(source) => <OverlayFactory data={source.data as DragData} />}
            </DragOverlay>
        </DragDropProvider>
    );
}

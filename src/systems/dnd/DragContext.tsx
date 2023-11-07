import {
    DndContext,
    type DragStartEvent,
    type DragEndEvent,
    DragOverlay,
    useSensors,
    useSensor,
    PointerSensor,
} from '@dnd-kit/core';
import React, { useState } from 'react';
import 'twin.macro';
import OverlayFactory from './OverlayFactory';
import { DragData, DropData } from './types';

interface Props {
    children: React.ReactNode;
}

export default function DragContext({ children }: Props): JSX.Element {
    const [activeData, setActiveData] = useState<DragData>();

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 12,
            },
        })
    );

    const handleDragStart = (event: DragStartEvent) => {
        const data = event.active.data.current as DragData;
        setActiveData(data);
    };

    const handleDragEnd = (event: DragEndEvent) => {
        const data = event.active.data.current as DragData;
        const target = event.over?.data.current as DropData;
        if (target && target.accepts(data)) {
            target.onDrop(data);
        }
        setActiveData(undefined);
    };

    return (
        <DndContext
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            sensors={sensors}
        >
            {children}
            <DragOverlay style={{ width: 'auto' }} tw="shadow-lg touch-none">
                {activeData ? <OverlayFactory data={activeData} /> : null}
            </DragOverlay>
        </DndContext>
    );
}

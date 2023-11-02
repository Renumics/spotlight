import {
    DndContext,
    DragStartEvent,
    DragEndEvent,
    DragOverlay,
    useSensors,
    useSensor,
    PointerSensor,
} from '@dnd-kit/core';
import React, { useState } from 'react';
import 'twin.macro';
import OverlayFactory from './OverlayFactory';
import { DragData } from './types';

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
        if (event.over?.data.current) {
            event.over.data.current.onDrop(data);
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
            <DragOverlay style={{ width: 'auto' }} tw="shadow-lg">
                {activeData ? <OverlayFactory data={activeData} /> : null}
            </DragOverlay>
        </DndContext>
    );
}

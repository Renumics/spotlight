import { useDraggable } from '@dnd-kit/core';
import { ReactNode, useId } from 'react';
import { DragData } from './types';

interface Props {
    data: DragData;
    children: ReactNode;
}

export default function Draggable({ data, children }: Props) {
    const id = useId();
    const { attributes, listeners, setNodeRef } = useDraggable({
        id,
        data,
    });
    return (
        <div ref={setNodeRef} {...listeners} {...attributes}>
            {children}
        </div>
    );
}

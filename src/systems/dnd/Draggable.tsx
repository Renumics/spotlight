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

    // remove tabIndex from attributes
    // as it prevents the keyboard controls of our table from working correctly
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { tabIndex, ...neededAttributes } = attributes;

    return (
        <div ref={setNodeRef} {...listeners} {...neededAttributes}>
            {children}
        </div>
    );
}

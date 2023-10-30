import { useDroppable } from '@dnd-kit/core';
import { ReactNode, useId } from 'react';
import { DragData } from './types';

interface Props {
    onDrop: (data: DragData) => void;
    children?: ReactNode;
    className?: string;
}

export default function Droppable({ onDrop, className, children }: Props): JSX.Element {
    const id = useId();
    const { setNodeRef } = useDroppable({
        id,
        data: {
            onDrop,
        },
    });

    return (
        <div className={className} ref={setNodeRef}>
            {children}
        </div>
    );
}

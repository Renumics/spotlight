import { useDroppable } from '@dnd-kit/core';
import { ReactNode, useId } from 'react';
import { DragData } from './types';

interface Props<Data extends DragData> {
    onDrop: (data: Data) => void;
    children?: ReactNode;
    className?: string;
}

export default function Droppable<Data extends DragData>({
    onDrop,
    className,
    children,
}: Props<Data>): JSX.Element {
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

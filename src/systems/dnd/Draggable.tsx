import { useDraggable } from '@dnd-kit/react';
import { ReactNode, useId } from 'react';
import { DragData } from './types';

interface Props {
    data: DragData;
    children: ReactNode;
}

export default function Draggable({ data, children }: Props) {
    const id = useId();
    const { ref } = useDraggable({
        id,
        data,
        type: data.kind,
    });

    return <div ref={ref}>{children}</div>;
}

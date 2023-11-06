import { useDroppable } from '@dnd-kit/core';
import { ReactNode, useId, useMemo } from 'react';
import { DragData } from './types';
import tw from 'twin.macro';

interface Props<Data extends DragData> {
    onDrop: (data: Data) => void;
    accepts?: (data: Data) => boolean;
    children?: ReactNode;
    className?: string;
}

export default function Droppable<Data extends DragData>({
    onDrop,
    accepts,
    className,
    children,
}: Props<Data>): JSX.Element {
    const id = useId();
    const { setNodeRef, isOver, active } = useDroppable({
        id,
        data: {
            onDrop,
        },
    });

    const data = active?.data.current;
    const isActive = useMemo(
        () => (!data ? false : accepts?.(data as Data) ?? true),
        [accepts, data]
    );

    return (
        <div
            className={className}
            ref={setNodeRef}
            css={[
                isActive && tw`ring-2 ring-blue-500/25 ring-inset`,
                isOver && tw`ring-green-500/50 ring-2`,
            ]}
        >
            {children}
        </div>
    );
}

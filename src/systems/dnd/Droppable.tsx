import { useDragOperation, useDroppable } from '@dnd-kit/react';
import { ReactNode, useId, useMemo } from 'react';
import { DragData } from './types';
import tw from 'twin.macro';

interface Props<Data extends DragData> {
    onDrop: (data: Data) => void;
    accepts?: (data: DragData) => boolean;
    children?: ReactNode;
    className?: string;
}

const acceptsAll = () => true;

export default function Droppable<Data extends DragData>({
    onDrop,
    accepts,
    className,
    children,
}: Props<Data>): JSX.Element {
    const id = useId();

    const dropData = {
        onDrop,
        accepts: accepts ?? acceptsAll,
    };

    const { ref, isDropTarget } = useDroppable({
        id,
        data: dropData,
        accept: ({ data }) => dropData.accepts(data as DragData),
    });

    const { source } = useDragOperation();
    const data = source?.data;
    const isActive = useMemo(
        () => (!data ? false : (accepts?.(data as Data) ?? true)),
        [accepts, data]
    );

    return (
        <div
            className={className}
            ref={ref}
            css={[
                isActive && tw`ring-2 ring-blue-500/25 ring-inset`,
                isActive && isDropTarget && tw`ring-green-500/50 ring-2`,
            ]}
        >
            {children}
        </div>
    );
}

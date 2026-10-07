import { useDraggable } from '@dnd-kit/react';
import { ReactNode, useEffect, useId, useState } from 'react';
import type { CellDragData } from '../../../systems/dnd';

interface DragSourceProps {
    data: CellDragData;
    element: HTMLElement;
}

/**
 * Makes the element a drag source of dnd-kit for as long as this component is mounted.
 */
const DragSource = ({ data, element }: DragSourceProps): null => {
    const id = useId();
    useDraggable({ id, data, type: data.kind, element });
    return null;
};

interface Props {
    data: CellDragData;
    children: ReactNode;
}

/** How long a cell stays in the table before it can be dragged without being entered */
const ARM_DELAY = 300;

/**
 * A table cell that can be dragged, to drop its value on the filter bar or a histogram.
 *
 * The table renders hundreds of cells, and every scroll renders new ones. Registering
 * all of them as drag sources with dnd-kit is most of the work of a scroll. So a cell
 * becomes a drag source when the pointer enters it, or when it has been in the table for
 * a moment, and stays one until it is removed from the table. Cells that are scrolled
 * past are never registered. The moment is for a pointer that does not enter a cell,
 * the one under it after a scroll, and for touch, where the pointer enters a cell with
 * the press that can start the drag: too late to start it.
 */
export default function DraggableCell({ data, children }: Props) {
    const [element, setElement] = useState<HTMLDivElement | null>(null);
    const [armed, setArmed] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setArmed(true), ARM_DELAY);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div ref={setElement} onPointerEnter={armed ? undefined : () => setArmed(true)}>
            {children}
            {armed && element && <DragSource data={data} element={element} />}
        </div>
    );
}

import { type DataColumn } from '../../types';
import EditIcon from '../../icons/Edit';
import 'twin.macro';
import DataTypeIcon from '../DataTypeIcon';
import { ColumnDragData } from '../../systems/dnd/types';
import Draggable from '../../systems/dnd/Draggable';
import { useDataset } from '../../stores/dataset';
import { type CSSProp } from 'styled-components';

interface InternalProps {
    column: DataColumn;
    className?: string;
    css?: CSSProp;
}

interface Props {
    columnKey: string;
    draggable?: boolean;
    className?: string;
    css?: CSSProp;
}

const StaticColumnBadge = ({ column, className }: InternalProps): JSX.Element => {
    return (
        <div
            tw="flex flex-row truncate rounded border text-xs text-midnight-500 bg-gray-100 p-0.5 hover:border-gray-600 transition space-x-0.5"
            className={className}
        >
            <DataTypeIcon type={column.type} />
            {column.editable && <EditIcon />}
            <span>{column.name}</span>
        </div>
    );
};

const ColumnBadge = ({
    columnKey,
    className,
    draggable = true,
}: Props): JSX.Element => {
    const column = useDataset((state) => state.columnsByKey[columnKey]);

    if (draggable) {
        const dragData: ColumnDragData = { kind: 'column', column };
        return (
            <Draggable data={dragData}>
                <StaticColumnBadge column={column} className={className} />
            </Draggable>
        );
    } else {
        return <StaticColumnBadge column={column} className={className} />;
    }
};

export default ColumnBadge;

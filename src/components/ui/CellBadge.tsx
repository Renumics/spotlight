import { type DataColumn } from '../../types';
import EditIcon from '../../icons/Edit';
import 'twin.macro';
import DataTypeIcon from '../DataTypeIcon';
import { ColumnDragData } from '../../systems/dnd/types';
import Draggable from '../../systems/dnd/Draggable';
import { useDataset } from '../../stores/dataset';
import { type CSSProp } from 'styled-components';
import dataformat from '../../dataformat';

interface InternalProps {
    column: DataColumn;
    row: number;
    className?: string;
    css?: CSSProp;
}

interface Props {
    columnKey: string;
    row: number;
    draggable?: boolean;
    className?: string;
    css?: CSSProp;
}

const StaticCellBadge = ({ column, row, className }: InternalProps): JSX.Element => {
    const tableData = useDataset((d) => d.columnData);
    const value = tableData[column.key][row];
    const formattedValue = dataformat.format(value, column.type);

    return (
        <div
            tw="flex flex-col rounded border text-xs text-midnight-500 bg-gray-100 p-0.5 hover:border-gray-600 transition space-x-0.5"
            className={className}
        >
            <div tw="flex flex-row">
                <DataTypeIcon type={column.type} />
                {column.editable && <EditIcon />}
                <span>{column.name}</span>
            </div>
            <span>Row {row}</span>
            <span>{formattedValue}</span>
        </div>
    );
};

const CellBadge = ({
    columnKey,
    row,
    className,
    draggable = true,
}: Props): JSX.Element => {
    const column = useDataset((state) => state.columnsByKey[columnKey]);

    if (draggable) {
        const dragData: ColumnDragData = { kind: 'column', column };
        return (
            <Draggable data={dragData}>
                <StaticCellBadge column={column} row={row} className={className} />
            </Draggable>
        );
    } else {
        return <StaticCellBadge column={column} row={row} className={className} />;
    }
};

export default CellBadge;

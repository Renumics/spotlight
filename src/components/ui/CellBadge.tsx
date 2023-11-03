import { type DataColumn } from '../../types';
import EditIcon from '../../icons/Edit';
import 'twin.macro';
import DataTypeIcon from '../DataTypeIcon';
import { ColumnDragData } from '../../systems/dnd/types';
import Draggable from '../../systems/dnd/Draggable';
import { useDataset } from '../../stores/dataset';
import { type CSSProp } from 'styled-components';
import ScalarValue from '../ScalarValue';

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

    return (
        <div
            tw="flex flex-col rounded border divide-y divide-gray-400 text-xs text-midnight-500 bg-gray-100 hover:border-gray-600 transition"
            className={className}
        >
            <div tw="flex flex-row divide-x">
                <div tw="flex flex-row p-1 space-x-0.5">
                    <DataTypeIcon type={column.type} />
                    {column.editable && <EditIcon />}
                    <span>{column.name}</span>
                </div>
                <div tw="flex justify-center items-center p-0.5 divide-gray-400">
                    {row}
                </div>
            </div>
            <div tw="p-1">
                <ScalarValue column={column} value={value} />
            </div>
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

import { type DataColumn } from '../../types';
import EditIcon from '../../icons/Edit';
import 'twin.macro';
import DataTypeIcon from '../DataTypeIcon';
import { ColumnDragData } from '../../systems/dnd/types';
import Draggable from '../../systems/dnd/Draggable';
import { useDataset } from '../../stores/dataset';
import { type CSSProp } from 'styled-components';
import Spinner from './Spinner';

interface InternalProps {
    column: DataColumn;
    computing: boolean;
    className?: string;
    css?: CSSProp;
}

interface Props {
    columnKey: string;
    draggable?: boolean;
    className?: string;
    css?: CSSProp;
}

const StaticColumnBadge = ({
    column,
    computing,
    className,
}: InternalProps): JSX.Element => {
    return (
        <div
            tw="flex flex-row truncate rounded border text-xs text-midnight-500 bg-gray-100 p-0.5 hover:border-gray-600 transition space-x-0.5"
            className={className}
        >
            <div tw="relative">
                <DataTypeIcon type={column.type} />
                {computing && (
                    <Spinner tw="h-2 w-2 bottom-0 right-0 absolute bg-gray-100 border-gray-100 text-gray-600 border" />
                )}
            </div>
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
    const computing = useDataset(
        (state) =>
            state.columnsByKey[columnKey].computed &&
            state.columnData[columnKey] === undefined
    );

    const badge = (
        <StaticColumnBadge
            column={column}
            computing={computing}
            className={className}
        />
    );

    if (draggable) {
        const dragData: ColumnDragData = { kind: 'column', column };
        return <Draggable data={dragData}>{badge}</Draggable>;
    } else {
        return badge;
    }
};

export default ColumnBadge;

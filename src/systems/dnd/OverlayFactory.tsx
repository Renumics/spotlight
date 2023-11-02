import 'twin.macro';
import EditIcon from '../../icons/Edit';
import { DragData } from './types';
import ColumnBadge from '../../components/ui/ColumnBadge';

interface Props {
    data: DragData;
}

export default function OverlayFactory({ data }: Props): JSX.Element {
    if (data.kind === 'column') {
        return <ColumnBadge columnKey={data.column.key} draggable={false} tw="p-1" />;
    }
    if (data.kind === 'cell') {
        return (
            <div tw="rounded text-xs bg-gray-200 py-0.5 px-1 border border-x border-gray-600 flex flex-row">
                <div>
                    {data.column.editable && <EditIcon tw="text-gray-400" />}
                    {data.column.name}
                </div>
                <div tw="pl-1 text-gray-800">[{data.row}]</div>
            </div>
        );
    }
    return <></>;
}

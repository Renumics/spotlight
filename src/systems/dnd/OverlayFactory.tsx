import 'twin.macro';
import EditIcon from '../../icons/Edit';
import { DragData } from './types';

interface Props {
    data: DragData;
}

export default function OverlayFactory({ data }: Props): JSX.Element {
    if (data.kind === 'column') {
        return (
            <div tw="rounded text-xs bg-gray-200 py-0.5 px-1 border border-x border-gray-600">
                {data.column.editable && <EditIcon tw="text-gray-400" />}{' '}
                {data.column.name}
            </div>
        );
    }
    if (data.kind === 'cell') {
        return (
            <div tw="rounded bg-gray-300 p-0.5">
                {data.column.name}[{data.row}]
            </div>
        );
    }
    return <></>;
}

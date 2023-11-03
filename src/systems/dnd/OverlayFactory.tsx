import 'twin.macro';
import { DragData } from './types';
import ColumnBadge from '../../components/ui/ColumnBadge';
import CellBadge from '../../components/ui/CellBadge';

interface Props {
    data: DragData;
}

export default function OverlayFactory({ data }: Props): JSX.Element {
    if (data.kind === 'column') {
        return <ColumnBadge columnKey={data.column.key} draggable={false} tw="p-1" />;
    }
    if (data.kind === 'cell') {
        return (
            <CellBadge
                columnKey={data.column.key}
                row={data.row}
                draggable={false}
                tw="p-1"
            />
        );
    }
    return <></>;
}

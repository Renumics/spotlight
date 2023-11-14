import { DataColumn } from '../../types';

export interface ColumnDragData {
    kind: 'column';
    column: DataColumn;
}

export interface CellDragData {
    kind: 'cell';
    column: DataColumn;
    row: number;
}

export type DragData = ColumnDragData | CellDragData;
export type DragKind = DragData['kind'];

export interface DropData {
    accepts: (data: DragData) => boolean;
    onDrop: (data: DragData) => void;
}

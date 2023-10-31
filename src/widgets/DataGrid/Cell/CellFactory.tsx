import { FunctionComponent, memo } from 'react';
import 'twin.macro';
import { useColumn } from '../context/columnContext';
import useCellValue from '../hooks/useCellValue';
import CategoricalCell from './CategoricalCell';
import DefaultCell from './DefaultCell';
import NumberCell from './NumberCell';
import { CellDragData, Draggable } from '../../../systems/dnd';
import useSort from '../hooks/useSort';

interface Props {
    columnIndex: number;
    rowIndex: number;
}

const CELL_COMPONENTS: Record<string, any> = {
    int: NumberCell,
    float: NumberCell,
    Category: CategoricalCell,
};

const CellFactory: FunctionComponent<Props> = ({ columnIndex, rowIndex }) => {
    const column = useColumn(columnIndex);
    const value = useCellValue(column?.key, rowIndex);
    const row = useSort().getOriginalIndex(rowIndex);

    if (column === undefined || column === null || value === null) return <></>;

    const CellComponent = CELL_COMPONENTS[column.type.kind] ?? DefaultCell;

    const dragData: CellDragData = {
        kind: 'cell',
        column,
        row,
    };

    return (
        <Draggable data={dragData}>
            <CellComponent column={column} value={value} />
        </Draggable>
    );
};

export default memo(CellFactory);

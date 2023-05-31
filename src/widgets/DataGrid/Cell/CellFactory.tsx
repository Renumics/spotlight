import { FunctionComponent, memo } from 'react';
import 'twin.macro';
import { CategoricalColumn, NumberColumn } from '../../../types';
import { useColumn } from '../context/columnContext';
import useCellValue from '../hooks/useCellValue';
import CategoricalCell from './CategoricalCell';
import DefaultCell from './DefaultCell';
import NumberCell from './NumberCell';

interface Props {
    columnIndex: number;
    rowIndex: number;
}

const CellFactory: FunctionComponent<Props> = ({ columnIndex, rowIndex }) => {
    const column = useColumn(columnIndex);

    const value = useCellValue(column?.key, rowIndex);

    if (column === undefined || column === null) return <></>;

    if (value === null) return <></>;

    switch (column.type.kind) {
        case 'int':
        case 'float':
            return <NumberCell column={column as NumberColumn} value={value} />;
        case 'Category':
            return (
                <CategoricalCell column={column as CategoricalColumn} value={value} />
            );
        default:
            return <DefaultCell column={column} value={value} />;
    }
};

export default memo(CellFactory);

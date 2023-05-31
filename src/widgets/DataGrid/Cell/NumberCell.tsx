import ScalarValue from '../../../components/ScalarValue';
import { FunctionComponent } from 'react';
import 'twin.macro';
import { NumberColumn } from '../../../types';
import { useTableView } from '../context/tableViewContext';

interface Props {
    column: NumberColumn;
    value: number;
}

const NumberCell: FunctionComponent<Props> = ({ value, column }) => {
    const { tableView } = useTableView();

    if (value === undefined || isNaN(value) || value === null) return <></>;

    return (
        <ScalarValue
            tw="w-full text-right"
            value={value}
            column={column}
            filtered={tableView !== 'full'}
        />
    );
};

export default NumberCell;

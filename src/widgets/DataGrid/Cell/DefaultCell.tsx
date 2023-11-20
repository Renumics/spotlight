import Tooltip from '../../../components/ui/Tooltip';
import { FunctionComponent } from 'react';
import { DataColumn } from '../../../types';
import { useDataformat } from '../../../dataformat';

interface Props {
    column: DataColumn;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value: any;
}

const DefaultCell: FunctionComponent<Props> = ({ value, column }) => {
    const formatter = useDataformat();
    const formattedValue = formatter.format(value, column?.type);
    const preciseValue = formatter.format(value, column?.type, true);

    return (
        <Tooltip content={preciseValue}>
            <div>{formattedValue}</div>
        </Tooltip>
    );
};

export default DefaultCell;

import Tooltip from '../../../components/ui/Tooltip';
import dataformat from '../../../dataformat';
import { FunctionComponent, useMemo } from 'react';
import { DataColumn } from '../../../types';

interface Props {
    column: DataColumn;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value: any;
}

const DefaultCell: FunctionComponent<Props> = ({ value, column }) => {
    const formattedValue = useMemo(
        () => dataformat.format(value, column?.type),
        [value, column?.type]
    );

    const preciseValue = useMemo(
        () => dataformat.format(value, column?.type, true),
        [value, column?.type]
    );

    return (
        <Tooltip content={preciseValue}>
            <div>{formattedValue}</div>
        </Tooltip>
    );
};

export default DefaultCell;

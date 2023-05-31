import Dot from '../../../components/ui/Dot';
import { FunctionComponent, useCallback, useMemo } from 'react';
import { Dataset, useDataset } from '../../../stores/dataset';
import 'twin.macro';
import { CategoricalColumn } from '../../../types';
import { useTableView } from '../context/tableViewContext';

interface Props {
    column: CategoricalColumn;
    value: number;
}

const CategoricalCell: FunctionComponent<Props> = ({ value, column }) => {
    const { tableView } = useTableView();

    const label = useMemo(
        () => (value !== undefined ? column.type.invertedCategories[value] : ''),
        [value, column.type]
    );

    const colorTransferFunctionSelector = useCallback(
        (d: Dataset) =>
            d.colorTransferFunctions[column.key]?.[
                tableView !== 'full' ? 'filtered' : 'full'
            ][0],
        [column.key, tableView]
    );

    const colorTransferFunction = useDataset(colorTransferFunctionSelector);
    const color = colorTransferFunction?.(value);

    if (label === undefined || isNaN(value) || value === null) return <></>;

    return (
        <div tw="w-full flex justify-end items-center">
            <span>{label}</span>
            {color && <Dot color={color.css()} />}
        </div>
    );
};

export default CategoricalCell;

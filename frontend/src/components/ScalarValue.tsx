import Dot from './ui/Dot';
import Tooltip from './ui/Tooltip';
import dataformat from '../dataformat';
import { isNumerical } from '../datatypes';
import { FunctionComponent, memo, useCallback, useMemo } from 'react';
import { Dataset, useDataset } from '../stores/dataset';
import tw, { styled } from 'twin.macro';
import { DataColumn } from '../types';

interface Props {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value?: any;
    className?: string;
    column: DataColumn;
    filtered?: boolean;
}

const FormattedValueSpan = styled.span(
    ({ isNumber = false }: { isNumber?: boolean }) => [
        tw`flex-grow overflow-hidden truncate`,
        isNumber && tw`text-right`,
    ]
);

const ScalarValue: FunctionComponent<Props> = ({
    value,
    className,
    column,
    filtered = false,
}) => {
    const formattedValue = useMemo(
        () => dataformat.format(value, column.type),
        [value, column.type]
    );
    const fullValue = useMemo(
        () => dataformat.format(value, column.type, true),
        [value, column.type]
    );
    const isNumber = isNumerical(column.type);

    // eslint-disable-next-line react-hooks/exhaustive-deps
    const colorTransferFunctionSelector = useCallback(
        (d: Dataset) =>
            d.colorTransferFunctions[column.key]?.[filtered ? 'filtered' : 'full'][0],
        [column.key, filtered]
    );

    const colorTransferFunction = useDataset(colorTransferFunctionSelector);
    const color = colorTransferFunction?.(value);

    return (
        <Tooltip content={`${fullValue}`}>
            <div className={className} tw="flex items-center">
                <FormattedValueSpan isNumber={isNumber}>
                    {formattedValue}
                </FormattedValueSpan>
                {color && <Dot color={color.css()} />}
            </div>
        </Tooltip>
    );
};

export default memo(ScalarValue);

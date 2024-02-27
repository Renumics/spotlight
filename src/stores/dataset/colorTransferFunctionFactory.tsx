import {
    createColorTransferFunction,
    TransferFunction,
} from '../../hooks/useColorTransferFunction';
import { DataColumn, TableData } from '../../types';
import { useColors } from '../colors';

type ColumnsTransferFunctions = Record<
    string,
    { full: TransferFunction; filtered: TransferFunction }
>;

export const makeColumnsColorTransferFunctions = (
    columns: DataColumn[],
    data: TableData,
    filteredIndices: Int32Array
): ColumnsTransferFunctions => {
    const colors = useColors.getState();

    return columns.reduce((a, column) => {
        const values = data[column.key];
        const filteredValues = new Array(filteredIndices.length);
        for (let i = 0; i < filteredIndices.length; ++i) {
            filteredValues[i] = data[column.key][filteredIndices[i]];
        }

        a[column.key] = {
            full: createColorTransferFunction(
                values,
                column.type,
                colors.robust,
                colors.continuousInts,
                colors.continuousCategories
            ),
            filtered: createColorTransferFunction(
                filteredValues,
                column.type,
                colors.robust,
                colors.continuousInts,
                colors.continuousCategories
            ),
        };
        return a;
    }, {} as ColumnsTransferFunctions);
};

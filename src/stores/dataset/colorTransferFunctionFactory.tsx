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
        a[column.key] = {
            full: createColorTransferFunction(
                data[column.key],
                column.type,
                colors.robust,
                colors.continuousInts,
                colors.continuousCategories
            ),
            filtered: createColorTransferFunction(
                filteredIndices.map((i) => data[column.key][i]),
                column.type,
                colors.robust,
                colors.continuousInts,
                colors.continuousCategories
            ),
        };
        return a;
    }, {} as ColumnsTransferFunctions);
};

import {
    DataType,
    isCategorical,
    isFloat,
    isNumerical,
    isScalar,
} from '../../datatypes';
import {
    createCategoricalTransferFunction,
    createConstantTransferFunction,
    createContinuousTransferFunction,
    TransferFunction,
} from '../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { useColors } from '../../stores/colors';
import {
    ColumnData,
    DataColumn,
    DataStatistics,
    isCategoricalColumn,
    isScalarColumn,
    TableData,
} from '../../types';
import { Dataset } from './dataset';

export const makeApplicableColorTransferFunctions = (
    type: DataType,
    data: ColumnData,
    stats?: DataStatistics
): TransferFunction[] => {
    const transferFunctions: TransferFunction[] = [];

    if ((isCategorical(type) || isScalar(type)) && !isFloat(type)) {
        const uniqueValues = _.uniq(data);
        const transFn = createCategoricalTransferFunction(uniqueValues, type);
        transferFunctions.push(transFn);
    }

    if (isNumerical(type)) {
        const useRobustColoring = useColors.getState().useRobustColorScales;

        const min = useRobustColoring ? stats?.p5 : stats?.min;
        const max = useRobustColoring ? stats?.p95 : stats?.max;

        transferFunctions.push(
            createContinuousTransferFunction(min || 0, max || 1, type)
        );
    }

    transferFunctions.push(createConstantTransferFunction(type));

    return transferFunctions;
};

type ColumnsTransferFunctions = Record<
    string,
    { full: TransferFunction[]; filtered: TransferFunction[] }
>;

export const makeColumnsColorTransferFunctions = (
    columns: DataColumn[],
    data: TableData,
    stats: Dataset['columnStats'],
    filteredMask: boolean[]
): ColumnsTransferFunctions => {
    return columns
        .filter((column) => isScalarColumn(column) || isCategoricalColumn(column))
        .reduce((a, column) => {
            a[column.key] = {
                full: makeApplicableColorTransferFunctions(
                    column.type,
                    data[column.key],
                    stats.full[column.key]
                ),
                filtered: makeApplicableColorTransferFunctions(
                    column.type,
                    data[column.key].filter((_, i) => filteredMask[i]),
                    stats.filtered[column.key]
                ),
            };
            return a;
        }, {} as ColumnsTransferFunctions);
};

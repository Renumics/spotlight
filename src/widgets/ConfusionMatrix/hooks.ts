import _ from 'lodash';
import { DataColumn, dataformat, useDataset } from '../../lib';
import { useMemo } from 'react';
import { ColumnData } from '../../types';
import type { MatrixData, Bucket } from './types';

export const useColumns = () => {
    return useDataset((d) => d.columns);
};

const useColumnValues = (key?: string, filtered: boolean = true) => {
    const indices = useDataset((d) => (filtered ? d.filteredIndices : d.indices));
    const columnData = useDataset((d) => d.columnData);

    return useMemo(
        () =>
            key === undefined ? [] : Array.from(indices).map((i) => columnData[key][i]),
        [indices, columnData, key]
    );
};

const useUniqueValues = (column?: DataColumn, data?: ColumnData) => {
    const names = useMemo(() => {
        if (!column) {
            return [];
        } else {
            switch (column.type.kind) {
                case 'bool':
                    return [true, false];
                case 'int':
                case 'str':
                    return _.sortedUniq(_.sortBy(data, _.identity));
                case 'Category':
                    const uniqValues = _.uniq(data);
                    return Object.values(column.type.categories).filter((cat) =>
                        uniqValues.includes(cat)
                    );
                default:
                    return _.sortedUniq(_.sortBy(data, _.identity));
            }
        }
    }, [column, data]);
    return names;
};

export function useData(
    xColumn?: DataColumn,
    yColumn?: DataColumn,
    filtered: boolean = true
): MatrixData {
    const xValues = useColumnValues(xColumn?.key, filtered);
    const yValues = useColumnValues(yColumn?.key, filtered);
    const uniqueXValues = useUniqueValues(xColumn, xValues);
    const uniqueYValues = useUniqueValues(yColumn, yValues);

    const indices = useDataset((d) => (filtered ? d.filteredIndices : d.indices));

    const buckets = useMemo(() => {
        const buckets: Bucket[] = new Array(uniqueXValues.length * uniqueYValues.length)
            .fill(null)
            .map(() => ({
                rows: [],
            }));
        for (let i = 0; i < xValues.length; ++i) {
            const x = uniqueXValues.indexOf(xValues[i]);
            const y = uniqueYValues.indexOf(yValues[i]);
            if (x == -1 || y == -1) continue;
            buckets[y * uniqueXValues.length + x].rows.push(indices[i]);
        }
        return buckets;
    }, [uniqueXValues, uniqueYValues, xValues, yValues, indices]);

    const xNames = useMemo(
        () =>
            xColumn
                ? uniqueXValues.map((value) => dataformat.format(value, xColumn.type))
                : [],
        [uniqueXValues, xColumn]
    );
    const yNames = useMemo(
        () =>
            yColumn
                ? uniqueYValues.map((value) => dataformat.format(value, yColumn.type))
                : [],
        [uniqueYValues, yColumn]
    );

    return {
        xNames,
        yNames,
        buckets,
    };
}

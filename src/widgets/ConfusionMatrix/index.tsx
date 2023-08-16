import 'twin.macro';
import _ from 'lodash';
import WidgetContainer from '../../components/ui/WidgetContainer';
import WidgetContent from '../../components/ui/WidgetContent';
import WidgetMenu from '../../components/ui/WidgetMenu';
import type { Widget } from '../types';
import { DataColumn, useDataset, useWidgetConfig } from '../../lib';
import TableIcon from '../../icons/Table';
import Matrix from './Matrix';
import ColumnSelect from '../../components/ui/Menu/ColumnSelect';
import { useMemo } from 'react';
import { ColumnData } from '../../types';

const COMPATIBLE_DATA_KINDS = ['int', 'Category', 'str', 'bool'];

const useColumns = () => {
    return useDataset((d) => d.columns);
};

const useColumnValues = (key?: string) => {
    return useDataset((d) => (key ? d.columnData[key] : [])) ?? [];
};

const useNames = (column: DataColumn | undefined, data: ColumnData) => {
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
                    return Object.values(column.type.categories);
                default:
                    return _.sortedUniq(_.sortBy(data, _.identity));
            }
        }
    }, [column, data]);
    return names;
};

function useData(xColumn: DataColumn, yColumn: DataColumn): MatrixData {
    const xValues = useColumnValues(xColumn.key);
    const yValues = useColumnValues(yColumn.key);
    const xNames = useNames(xColumn, xValues);
    const yNames = useNames(yColumn, yValues);

    const buckets = useMemo(() => {
        const buckets: Bucket[] = new Array(xNames.length * yNames.length)
            .fill(null)
            .map(() => ({
                x: 0,
                y: 0,
                rows: [],
            }));
        for (let i = 0; i < xValues.length; ++i) {
            const x = xNames.indexOf(xValues[i]);
            const y = yNames.indexOf(yValues[i]);
            if (x == -1 || y == -1) continue;
            buckets[y * xNames.length + x].rows.push(i);
        }
        return buckets;
    }, [xNames, xValues, yNames, yValues]);

    return {
        xNames,
        yNames,
        buckets,
    };
}

const ConfusionMatrix: Widget = () => {
    const [xKey, setXKey] = useWidgetConfig<string>('xColumn');
    const [yKey, setYKey] = useWidgetConfig<string>('yColumn');

    const columns = useColumns();
    const compatibleColumns = columns.filter((c) =>
        COMPATIBLE_DATA_KINDS.includes(c.type.kind)
    );
    const compatibleColumnKeys = compatibleColumns.map((c) => c.key);
    const xColumn = compatibleColumns.filter((c) => c.key === xKey)[0];
    const yColumn = compatibleColumns.filter((c) => c.key === yKey)[0];

    const data = useData(xColumn, yColumn);

    return (
        <WidgetContainer>
            <WidgetMenu>
                <div tw="w-32 h-full flex">
                    <ColumnSelect
                        selectableColumns={compatibleColumnKeys}
                        onChangeColumn={setXKey}
                        selected={xKey}
                        title="x"
                        variant="inset"
                    />
                </div>
                <div tw="w-32 h-full flex">
                    <ColumnSelect
                        selectableColumns={compatibleColumnKeys}
                        onChangeColumn={setYKey}
                        selected={yKey}
                        title="y"
                        variant="inset"
                    />
                </div>
            </WidgetMenu>
            <WidgetContent tw="bg-white overflow-hidden">
                <Matrix data={data} />
            </WidgetContent>
        </WidgetContainer>
    );
};

ConfusionMatrix.key = 'ConfusionMatrix';
ConfusionMatrix.defaultName = 'Confusion Matrix';
ConfusionMatrix.icon = TableIcon;

export default ConfusionMatrix;

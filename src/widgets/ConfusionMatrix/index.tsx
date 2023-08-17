import 'twin.macro';
import WidgetContainer from '../../components/ui/WidgetContainer';
import WidgetContent from '../../components/ui/WidgetContent';
import WidgetMenu from '../../components/ui/WidgetMenu';
import type { Widget } from '../types';
import { useDataset, useWidgetConfig } from '../../lib';
import GridIcon from '../../icons/Grid';
import Matrix from './Matrix';
import ColumnSelect from '../../components/ui/Menu/ColumnSelect';
import { useCallback } from 'react';
import type { Cell } from './types';
import { useColumns, useData } from './hooks';

const COMPATIBLE_DATA_KINDS = ['int', 'Category', 'str', 'bool'];

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

    const handleHoverCell = useCallback((cell?: Cell) => {
        if (!cell) return;
        useDataset.getState().highlightRows(cell.bucket.rows);
    }, []);

    const handleClickCell = useCallback((cell?: Cell) => {
        if (!cell) return;
        useDataset.getState().selectRows(cell.bucket.rows);
    }, []);

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
                <Matrix
                    data={data}
                    onHoverCell={handleHoverCell}
                    onClickCell={handleClickCell}
                />
            </WidgetContent>
        </WidgetContainer>
    );
};

ConfusionMatrix.key = 'ConfusionMatrix';
ConfusionMatrix.defaultName = 'Confusion Matrix';
ConfusionMatrix.icon = GridIcon;

export default ConfusionMatrix;

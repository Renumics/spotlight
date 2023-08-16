import 'twin.macro';
import { useMemo } from 'react';
import WidgetContainer from '../../components/ui/WidgetContainer';
import WidgetContent from '../../components/ui/WidgetContent';
import WidgetMenu from '../../components/ui/WidgetMenu';
import type { Widget } from '../types';
import { useDataset, useWidgetConfig } from '../../lib';
import TableIcon from '../../icons/Table';
import Matrix from './Matrix';

const useColumns = (keys: string[]) => {
    const allColumns = useDataset((d) => d.columns);
    return useMemo(
        () => allColumns.filter((c) => keys.includes(c.key)),
        [allColumns, keys]
    );
};

const ConfusionMatrix: Widget = () => {
    const [visibleColumnKeys, setVisibleColumnKeys] = useWidgetConfig<string[]>(
        'visibleColumns',
        []
    );
    const columns = useColumns(visibleColumnKeys);

    return (
        <WidgetContainer>
            <WidgetMenu></WidgetMenu>
            <WidgetContent tw="bg-white overflow-hidden">
                <Matrix
                    xNames={['x', 'y']}
                    yNames={['a', 'b']}
                    data={[0.9, 0.1, 0.2, 0.8]}
                />
            </WidgetContent>
        </WidgetContainer>
    );
};

ConfusionMatrix.key = 'ConfusionMatrix';
ConfusionMatrix.defaultName = 'Confusion Matrix';
ConfusionMatrix.icon = TableIcon;

export default ConfusionMatrix;

import 'twin.macro';
import DetailsIcon from '../../icons/ClipboardList';
import AutoSizer, { Size } from 'react-virtualized-auto-sizer';
import { Widget } from '../types';
import useWidgetConfig from '../useWidgetConfig';
import DetailsGrid, { COLUMN_COUNT_OPTIONS } from './DetailsGrid';
import MenuBar from './MenuBar';
import { StoreProvider, useStore } from './store';
import { WidgetContainer, WidgetContent } from '../../lib';
import Droppable from '../../systems/dnd/Droppable';
import { isLensCompatible, useComponentsStore } from '../../stores/components';
import { DragData } from '../../systems/dnd/types';

const DropZone = () => {
    const addView = useStore((state) => state.addView);

    const handleDrop = ({ column }: DragData) => {
        const lens = useComponentsStore
            .getState()
            .lenses.filter(
                (lens) =>
                    isLensCompatible(lens, [column.type], column.editable) &&
                    (lens.isSatisfied?.([column]) ?? true)
            )[0];
        addView({
            view: lens.key,
            columns: [column.key],
            name: 'view',
            key: crypto.randomUUID(),
        });
    };

    return (
        <Droppable
            tw="absolute w-full h-full z-10 pointer-events-none"
            onDrop={handleDrop}
        />
    );
};

const Inspector: Widget = () => {
    const [visibleColumnsCount, setVisibleColumnsCount] = useWidgetConfig(
        'visibleColumns',
        4
    );
    return (
        <StoreProvider>
            <WidgetContainer>
                <MenuBar
                    visibleColumnsCount={visibleColumnsCount}
                    setVisibleColumnsCount={setVisibleColumnsCount}
                    visibleColumnsCountOptions={COLUMN_COUNT_OPTIONS}
                />
                <WidgetContent>
                    <DropZone />
                    <AutoSizer>
                        {({ width, height }: Size) => (
                            <DetailsGrid
                                width={width}
                                height={height}
                                visibleColumnsCount={visibleColumnsCount}
                            />
                        )}
                    </AutoSizer>
                </WidgetContent>
            </WidgetContainer>
        </StoreProvider>
    );
};

Inspector.defaultName = 'Inspector';
Inspector.icon = DetailsIcon;
Inspector.key = 'inspector';
Inspector.legacyKeys = ['details'];

export default Inspector;

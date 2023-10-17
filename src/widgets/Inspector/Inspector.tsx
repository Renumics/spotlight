import 'twin.macro';
import DetailsIcon from '../../icons/ClipboardList';
import AutoSizer from 'react-virtualized-auto-sizer';
import { Widget } from '../types';
import useWidgetConfig from '../useWidgetConfig';
import DetailsGrid, { COLUMN_COUNT_OPTIONS } from './DetailsGrid';
import MenuBar from './MenuBar';
import { StoreProvider } from './store';
import { WidgetContainer, WidgetContent } from '../../lib';

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
                    <AutoSizer>
                        {({ width, height }) => (
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

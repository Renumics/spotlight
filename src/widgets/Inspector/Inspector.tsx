import DetailsIcon from '../../icons/ClipboardList';
import AutoSizer from 'react-virtualized-auto-sizer';
import tw from 'twin.macro';
import { Widget } from '../types';
import useWidgetConfig from '../useWidgetConfig';
import { DataContext, DataProvider } from './dataContext';
import DetailsGrid, { COLUMN_COUNT_OPTIONS } from './DetailsGrid';
import MenuBar from './MenuBar';
import { StoreProvider } from './store';

const Wrapper = tw.div`w-full h-full flex flex-col overflow-hidden`;
const GridContainer = tw.div`flex-auto`;

const Inspector: Widget = () => {
    const [visibleColumnsCount, setVisibleColumnsCount] = useWidgetConfig(
        'visibleColumns',
        4
    );
    return (
        <StoreProvider>
            <DataProvider>
                <DataContext.Consumer>
                    {() => (
                        <Wrapper>
                            <MenuBar
                                visibleColumnsCount={visibleColumnsCount}
                                setVisibleColumnsCount={setVisibleColumnsCount}
                                visibleColumnsCountOptions={COLUMN_COUNT_OPTIONS}
                            />

                            <GridContainer>
                                <AutoSizer>
                                    {({ width, height }) => (
                                        <DetailsGrid
                                            width={width}
                                            height={height}
                                            visibleColumnsCount={visibleColumnsCount}
                                        />
                                    )}
                                </AutoSizer>
                            </GridContainer>
                        </Wrapper>
                    )}
                </DataContext.Consumer>
            </DataProvider>
        </StoreProvider>
    );
};

Inspector.defaultName = 'Inspector';
Inspector.icon = DetailsIcon;
Inspector.key = 'inspector';
Inspector.legacyKeys = ['details'];

export default Inspector;

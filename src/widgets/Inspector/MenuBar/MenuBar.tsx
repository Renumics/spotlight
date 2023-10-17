import 'twin.macro';
import { FunctionComponent } from 'react';
import AddViewButton from '../AddViewButton';
import ColumnCountSelect from './ColumnCountSelect';
import { WidgetMenu } from '../../../lib';

interface Props {
    visibleColumnsCount: number;
    setVisibleColumnsCount: (count: number) => void;
    visibleColumnsCountOptions: number[];
}

const MenuBar: FunctionComponent<Props> = ({
    visibleColumnsCount,
    setVisibleColumnsCount,
    visibleColumnsCountOptions,
}) => {
    return (
        <WidgetMenu>
            <div tw="flex-grow" />
            <ColumnCountSelect
                visibleColumnsCount={visibleColumnsCount}
                setVisibleColumnsCount={setVisibleColumnsCount}
                visibleColumnsCountOptions={visibleColumnsCountOptions}
            />
            <AddViewButton />
        </WidgetMenu>
    );
};

export default MenuBar;

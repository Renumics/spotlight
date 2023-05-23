import { FunctionComponent } from 'react';
import tw from 'twin.macro';
import AddViewButton from '../AddViewButton';
import ColumnCountSelect from './ColumnCountSelect';

const Styles = tw.div`pl-1 py-0.5 flex flex-row border-b border-gray-400 text-sm h-6 justify-end items-center`;
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
        <Styles>
            <ColumnCountSelect
                visibleColumnsCount={visibleColumnsCount}
                setVisibleColumnsCount={setVisibleColumnsCount}
                visibleColumnsCountOptions={visibleColumnsCountOptions}
            />
            <AddViewButton />
        </Styles>
    );
};

export default MenuBar;

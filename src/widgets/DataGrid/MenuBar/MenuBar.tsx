import ColumnSelector from '../../../components/ColumnSelector';
import VisibleIcon from '../../../icons/Show';
import Button from '../../../components/ui/Button';
import Dropdown from '../../../components/ui/Dropdown';
import Menu from '../../../components/ui/Menu';
import { FunctionComponent, useCallback, useContext } from 'react';
import tw from 'twin.macro';
import { DataColumn } from '../../../types';
import { ColumnContext } from '../context/columnContext';
import Settings from './SettingsMenu';
import TableViewSelection from './TableViewSelection';
import AddColumnButton from './AddColumnButton';

const Styles = tw.div`pl-1 py-0.5 flex flex-row border-b border-gray-400 text-sm`;
const Spacer = tw.div`flex-grow`;

const MenuBar: FunctionComponent = () => {
    const { setColumnKeys, columns, allColumns, resetColumns } =
        useContext(ColumnContext);

    const onChangeColumns = useCallback(
        (cols: DataColumn[]) => {
            const keys = cols.map((col) => col.key);
            setColumnKeys(keys);
        },
        [setColumnKeys]
    );

    const selectAllColumns = useCallback(() => {
        const keys = allColumns.map((col) => col.key);
        setColumnKeys(keys);
    }, [setColumnKeys, allColumns]);

    const selectNoColumn = useCallback(() => setColumnKeys([]), [setColumnKeys]);

    const menu = (
        <Menu tw="w-96">
            <Menu.Title>
                <span>Visible Columns</span>
            </Menu.Title>
            <ColumnSelector
                availableColumns={allColumns}
                columns={columns}
                onChange={onChangeColumns}
            />
            <div tw="flex flex-row text-xs items-center">
                <Button
                    tw="border-r border-gray-400 py-1 w-16"
                    onClick={selectAllColumns}
                >
                    All
                </Button>
                <Button
                    tw="border-r border-gray-400 py-1 w-16"
                    onClick={selectNoColumn}
                >
                    None
                </Button>
                <Button tw="border-r border-gray-400 py-1 w-16" onClick={resetColumns}>
                    Default
                </Button>
                <div tw="flex-grow text-right px-1 text-gray-600">
                    {columns.length}/{allColumns.length}
                </div>
            </div>
        </Menu>
    );

    return (
        <Styles>
            <TableViewSelection />
            <Spacer />
            <AddColumnButton />
            <Dropdown tw="font-normal" content={menu} tooltip="Visible Columns">
                <div tw="flex flex-row items-center text-xs">
                    <VisibleIcon />
                </div>
            </Dropdown>
            <Settings />
        </Styles>
    );
};

export default MenuBar;

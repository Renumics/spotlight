import _ from 'lodash';
import {
    ChangeEvent,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import tw from 'twin.macro';
import dataformat from '../../dataformat';
import X from '../../icons/X';
import { DataColumn } from '../../types';
import { DropdownContext } from '../ui/Dropdown';
import Menu from '../ui/Menu';
import ColumnList from './ColumnList';
import ColumnListItem from './ColumnListItem';
import ColumnListSeparator from './ColumnListSeparator';

interface Props {
    availableColumns: DataColumn[];
    columns: DataColumn[];
    onChange?: (columns: DataColumn[]) => void;
}

const ColumnSelector = ({
    availableColumns,
    columns,
    onChange,
}: Props): JSX.Element => {
    const searchRef = useRef<HTMLInputElement>(null);
    const { visible } = useContext(DropdownContext);

    const [searchTerm, setSearchTerm] = useState('');

    const filteredColumns = useMemo(() => {
        if (!searchTerm) return availableColumns;

        const regex = new RegExp(searchTerm, 'i');

        return availableColumns.filter(
            (c) =>
                regex.test(c.name) ||
                regex.test(c.type.kind) ||
                regex.test(dataformat.formatType(c.type)) ||
                regex.test(dataformat.formatType(c.type, true)) ||
                c.tags?.some((tag) => regex.test(tag))
        );
    }, [availableColumns, searchTerm]);

    const remainingColumns = useMemo(
        () => _.difference(filteredColumns, columns),
        [filteredColumns, columns]
    );

    const handleColumnSelect = useCallback(
        (column: DataColumn, selected: boolean) => {
            if (selected) {
                //add column to selection
                const newColumns = columns.includes(column)
                    ? columns
                    : [...columns, column];
                onChange?.(newColumns);
            } else {
                //remove column from selection
                const remainingColumns = columns.filter((col) => col !== column);
                onChange?.(remainingColumns);
            }
        },
        [columns, onChange]
    );

    useEffect(() => {
        if (visible) searchRef.current?.focus();
    }, [visible]);

    const onClickClear = useMemo(
        () => (searchTerm ? () => setSearchTerm('') : undefined),
        [searchTerm]
    );

    return (
        <>
            <Menu.ActionInput
                ref={searchRef}
                onClickAction={onClickClear}
                actionIcon={<X />}
                placeholder="Search column/type/tag"
                value={searchTerm}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    setSearchTerm(e.target.value)
                }
            />
            <ColumnList>
                {columns.map((col) => (
                    <ColumnListItem
                        key={col.key}
                        column={col}
                        selected={true}
                        onChangeSelected={handleColumnSelect}
                    />
                ))}
                <ColumnListSeparator
                    css={[
                        !(columns.length && remainingColumns.length) && tw`invisible`,
                    ]}
                />
                {remainingColumns.map((col) => (
                    <ColumnListItem
                        key={col.key}
                        column={col}
                        selected={false}
                        onChangeSelected={handleColumnSelect}
                    />
                ))}
            </ColumnList>
        </>
    );
};

export default ColumnSelector;

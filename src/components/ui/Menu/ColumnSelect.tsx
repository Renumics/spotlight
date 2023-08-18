import { FunctionComponent, memo, useCallback, useMemo } from 'react';
import { Dataset, useDataset } from '../../../stores/dataset';
import { shallow } from 'zustand/shallow';
import Menu from '.';
import Select from '../Select';
import { SelectVariant } from '../Select/types';

export interface Props {
    title: string;
    selected?: string;
    selectableColumns: string[];
    onChangeColumn: (keys: string) => void;
    variant?: SelectVariant;
}

const columnNamesSelector = (d: Dataset) =>
    d.columns.reduce((a: { [key: string]: string }, c) => {
        a[c.key] = c.name;
        return a;
    }, {});

const ColumnSelect: FunctionComponent<Props> = (props) => {
    const { title, selected, selectableColumns, onChangeColumn, variant } = props;
    const columnNames = useDataset(columnNamesSelector, shallow);

    const selectOptions = useMemo(
        () => [null, ...selectableColumns],
        [selectableColumns]
    );

    const onChangeColumnCallback = useCallback(
        (key?: string | null) => {
            onChangeColumn(key ?? '');
        },
        [onChangeColumn]
    );

    const getColumnName = useCallback(
        (key: string | undefined | null) => (key ? columnNames[key] : 'None'),
        [columnNames]
    );

    return (
        <>
            <Menu.Title>{title}</Menu.Title>
            <Menu.Item>
                <Select
                    value={selected}
                    onChange={onChangeColumnCallback}
                    options={selectOptions}
                    label={getColumnName}
                    variant={variant}
                />
            </Menu.Item>
        </>
    );
};

export default memo(ColumnSelect);

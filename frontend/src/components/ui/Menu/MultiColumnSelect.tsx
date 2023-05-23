import Warning from '../../../icons/Warning';
import { FunctionComponent, useCallback, useMemo } from 'react';
import Select, { components } from 'react-select';
import type { MultiValue, MultiValueGenericProps } from 'react-select';
import { Dataset, useDataset } from '../../../stores/dataset';
import tw from 'twin.macro';
import { shallow } from 'zustand/shallow';
import Menu from '.';
import Tooltip from '../Tooltip';

export interface Hint {
    type: 'warning';
    message: React.ReactNode;
}

export interface Props {
    title: string;
    selected?: string[];
    selectableColumns: string[];
    columnHints?: { [columnKey: string]: Hint };
    onChangeColumn: (keys: string[]) => void;
}

const columnNamesSelector = (d: Dataset) =>
    d.columns.reduce((a: { [key: string]: string }, c) => {
        a[c.key] = c.name;
        return a;
    }, {});

interface ValueOption {
    value?: string;
    hint?: Hint;
}

const MultiValueLabel = (props: MultiValueGenericProps<ValueOption>) => {
    const hint: Hint = props.data.hint;
    return (
        <div tw="flex items-center">
            <components.MultiValueLabel {...props} />
            {hint !== undefined && hint.type === 'warning' && (
                <Tooltip content={hint.message}>
                    <Warning />
                </Tooltip>
            )}
        </div>
    );
};

const MultiColumnSelect: FunctionComponent<Props> = (props) => {
    const { title, selected, selectableColumns, columnHints, onChangeColumn } = props;
    const columnNames = useDataset(columnNamesSelector, shallow);

    const selectOptions = useMemo(
        () =>
            selectableColumns.map((key) => ({ value: key, hint: columnHints?.[key] })),
        [columnHints, selectableColumns]
    );
    const selectedOptions = useMemo(
        () => selected?.map((key) => ({ value: key, hint: columnHints?.[key] })) || [],
        [columnHints, selected]
    );

    const handleChange = useCallback(
        (options: MultiValue<ValueOption>) => {
            const changed = options.filter((option) => option.value !== undefined) as {
                value: string;
            }[];
            onChangeColumn(changed.map((option) => option.value));
        },
        [onChangeColumn]
    );

    const getColumnName = useCallback(
        ({ value }: { value?: string }) => (value ? columnNames[value] : 'None'),
        [columnNames]
    );

    const menuPortalTarget = document.getElementById('selectMenuRoot');
    if (menuPortalTarget === null) return <></>;

    return (
        <>
            <Menu.Title>{title}</Menu.Title>
            <Menu.Item>
                <Select<ValueOption, true>
                    components={{ MultiValueLabel }}
                    value={selectedOptions}
                    onChange={handleChange}
                    getOptionLabel={getColumnName}
                    options={selectOptions}
                    isMulti={true}
                    menuPortalTarget={menuPortalTarget}
                    styles={{
                        option: (provided) => ({
                            ...provided,
                            ...tw`text-xs`,
                        }),
                    }}
                />
            </Menu.Item>
        </>
    );
};

export default MultiColumnSelect;

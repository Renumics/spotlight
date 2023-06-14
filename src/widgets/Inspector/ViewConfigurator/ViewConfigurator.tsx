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
import tw, { styled } from 'twin.macro';
import { v4 as uuidv4 } from 'uuid';
import Button from '../../../components/ui/Button';
import { DropdownContext } from '../../../components/ui/Dropdown';
import Menu from '../../../components/ui/Menu';
import Select from '../../../components/ui/Select';
import dataformat from '../../../dataformat';
import { DataKind } from '../../../datatypes';
import { X } from '../../../icons';
import { isLensCompatible, useComponentsStore } from '../../../stores/components';
import { Dataset, useDataset } from '../../../stores/dataset';
import { DataColumn, LensKey } from '../../../types';
import { useStore } from '../store';
import ColumnList from './ColumnList';
import ColumnListItem from './ColumnListItem';
import ColumnListSeparator from './ColumnListSeparator';

const columnsSelector = (d: Dataset) => d.columns;

// this styling is neaded in order to increase specificity as Menu defines specific styles for its label children
const LightColumnListItem = styled(ColumnListItem)`
    && {
        ${tw`text-gray-800`}
    }
`;

const ViewConfigurator = (): JSX.Element => {
    const searchRef = useRef<HTMLInputElement>(null);
    const { hide, visible } = useContext(DropdownContext);
    const allColumns = useDataset(columnsSelector);
    const addView = useStore((state) => state.addView);

    const lenses = useComponentsStore((state) => state.lensesByKey);

    const [columns, setColumns] = useState<string[]>([]);

    const [view, setView] = useState<LensKey | null>();

    const [searchTerm, setSearchTerm] = useState('');

    const filteredColumns = useMemo(() => {
        if (!searchTerm) return allColumns;

        const regex = new RegExp(searchTerm, 'i');
        return allColumns.filter(
            (c) =>
                regex.test(c.name) ||
                regex.test(c.type.kind) ||
                regex.test(dataformat.formatType(c.type)) ||
                regex.test(dataformat.formatType(c.type, true)) ||
                c.tags?.some((tag) => regex.test(tag))
        );
    }, [allColumns, searchTerm]);

    const selectedColumns = useMemo(
        () => _.compact(columns.map((k) => filteredColumns.find((c) => c.key === k))),
        [columns, filteredColumns]
    );

    const compatibleViews = useMemo(() => {
        const columnTypes = selectedColumns.map((c) => c.type);
        const allEditable = selectedColumns.every((c) => c.editable);
        return Object.values(lenses)
            .filter((lens) => isLensCompatible(lens, columnTypes, allEditable))
            .map((lens) => lens.key);
    }, [selectedColumns, lenses]);

    const isViewCompatible = view && compatibleViews.includes(view);
    const compatibleView = useMemo(
        () => (isViewCompatible ? view : compatibleViews[0]),
        [compatibleViews, isViewCompatible, view]
    );
    const isViewSatisfied =
        lenses[compatibleView]?.isSatisfied?.(selectedColumns) ?? true;

    const [compatibleColumns, allCompatibleColumns] = useMemo(() => {
        if (!columns.length) return [filteredColumns, filteredColumns];

        const dtypes = new Set<DataKind>();
        const allAllowedColumns = new Set<DataColumn>();
        compatibleViews.forEach((lensKey: LensKey) => {
            const view = lenses[lensKey];
            const cols = view.filterAllowedColumns?.(allColumns, selectedColumns);
            if (cols) {
                cols.forEach((col) => allAllowedColumns.add(col));
            } else if (view.multi) {
                view.dataTypes.forEach((d) => dtypes.add(d));
            }
        });

        return [
            filteredColumns.filter(
                (c) =>
                    !columns.includes(c.key) &&
                    (dtypes.has(c.type.kind) || allAllowedColumns.has(c))
            ),
            Array.from(allAllowedColumns).filter((c) => !columns.includes(c.key)),
        ];
    }, [
        filteredColumns,
        selectedColumns,
        columns,
        compatibleViews,
        allColumns,
        lenses,
    ]);

    const handleAdd = useCallback(() => {
        if (!compatibleView || !columns.length) return;
        addView({
            view: compatibleView,
            columns,
            name: 'view',
            key: uuidv4(),
        });
        setColumns([]);
        setView(undefined);
        setSearchTerm('');
        hide();
    }, [addView, columns, hide, compatibleView]);

    const deselectColumn = useCallback((key: string) => {
        setColumns((columns) => columns.filter((k) => k !== key));
    }, []);

    const handleColumnSelect = useCallback(
        (column: DataColumn, selected: boolean) => {
            if (selected) {
                setColumns((columns) =>
                    columns.includes(column.key) ? columns : [...columns, column.key]
                );
            } else {
                deselectColumn(column.key);
            }
        },
        [deselectColumn]
    );

    useEffect(() => {
        if (visible) searchRef.current?.focus();
    }, [visible]);

    const onClickClear = useMemo(
        () => (searchTerm ? () => setSearchTerm('') : undefined),
        [searchTerm]
    );

    return (
        <Menu tw="flex flex-col p-0 m-0 w-96">
            <Menu.Title tw="px-1 pt-1 pb-0">Columns</Menu.Title>
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
                {selectedColumns.map((col) => (
                    <ColumnListItem
                        key={col.key}
                        column={col}
                        selected={true}
                        onChangeSelected={handleColumnSelect}
                    />
                ))}
                <ColumnListSeparator
                    css={[
                        !(selectedColumns.length && compatibleColumns.length) &&
                            tw`invisible`,
                    ]}
                />
                {compatibleColumns.length > 0
                    ? compatibleColumns.map((col) => (
                          <ColumnListItem
                              key={col.key}
                              column={col}
                              selected={false}
                              onChangeSelected={handleColumnSelect}
                          />
                      ))
                    : searchTerm &&
                      allCompatibleColumns.map((col) => (
                          <LightColumnListItem
                              key={col.key}
                              column={col}
                              selected={false}
                              onChangeSelected={handleColumnSelect}
                          />
                      ))}
            </ColumnList>
            <Menu.Title tw="px-1 py-0">Views</Menu.Title>
            <div tw="p-1">
                <Select
                    options={compatibleViews}
                    onChange={setView}
                    value={compatibleView}
                    label={(viewKey) =>
                        viewKey ? lenses[viewKey].displayName ?? viewKey : ''
                    }
                    isDisabled={!compatibleViews.length}
                />
            </div>
            <div tw="flex flex-row justify-end p-1">
                <Button
                    tw="bg-green-600 text-white p-1 rounded w-auto disabled:bg-gray-200 disabled:hover:bg-gray-200 disabled:text-gray-500 disabled:hover:text-gray-500 hover:bg-green-200 hover:text-white"
                    disabled={!compatibleView || !isViewSatisfied || !columns.length}
                    onClick={handleAdd}
                >
                    Add View
                </Button>
            </div>
        </Menu>
    );
};

export default ViewConfigurator;

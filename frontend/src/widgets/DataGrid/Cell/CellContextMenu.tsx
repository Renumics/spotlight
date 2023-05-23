import AddIcon from '../../../icons/Add';
import CheckedIcon from '../../../icons/Checked';
import DeleteIcon from '../../../icons/Delete';
import EditIcon from '../../../icons/Edit';
import FilterIcon from '../../../icons/Filter';
import HideIcon from '../../../icons/Hide';
import UncheckedIcon from '../../../icons/Unchecked';
import Button from '../../../components/ui/Button';
import { useContextMenu } from '../../../components/ui/ContextMenu';
import Menu from '../../../components/ui/Menu';
import { isBoolean } from '../../../datatypes';
import { getApplicablePredicates } from '../../../filters';
import { ComponentProps, FunctionComponent, useCallback, useMemo } from 'react';
import { useDataset } from '../../../stores/dataset';
import 'twin.macro';
import { DataColumn, IndexArray, PredicateFilter } from '../../../types';
import { useColumn, useVisibleColumns } from '../context/columnContext';
import useCellValue from '../hooks/useCellValue';
import NeedsUpgradeButton from '../../../components/ui/NeedsUpgradeButton';

export interface Props {
    columnIndex: number;
    rowIndex: number;
    onDeleteColumn?: () => void;
    onDeleteRow?: () => void;
    onDuplicateRow?: () => void;
    onDoEdit?: (column: DataColumn, rowIndices: IndexArray) => void;
}

interface ActionProps {
    caption: string;
    icon: JSX.Element;
    disabled?: ComponentProps<typeof Button>['disabled'];
    onClick?: ComponentProps<typeof Button>['onClick'];
    needsUpgrade?: boolean;
}
const Action = ({ caption, icon, disabled, onClick, needsUpgrade }: ActionProps) => {
    const ButtonComponent = needsUpgrade ? NeedsUpgradeButton : Button;
    return (
        <Menu.Item>
            <ButtonComponent onClick={onClick} disabled={disabled ?? needsUpgrade}>
                {icon}
                <span tw="ml-1 font-normal">{caption}</span>
            </ButtonComponent>
        </Menu.Item>
    );
};

const CellContextMenu: FunctionComponent<Props> = ({ columnIndex, rowIndex }) => {
    const column = useColumn(columnIndex);

    const [, , hideColumn] = useVisibleColumns();
    const value = useCellValue(column.key, rowIndex);

    const addFilter = useDataset((d) => d.addFilter);
    const { hide: hideContextMenu } = useContextMenu();

    const canBeFiltered = useMemo(
        () =>
            column !== undefined &&
            value !== undefined &&
            getApplicablePredicates(column.type.kind).equal !== undefined,
        [column, value]
    );

    const onClickFilter = useCallback(() => {
        hideContextMenu();
        if (!canBeFiltered || !column) return;

        const operation = getApplicablePredicates(column.type.kind).equal;
        const newFilter = new PredicateFilter(column, operation, value);

        addFilter(newFilter);
    }, [addFilter, canBeFiltered, column, hideContextMenu, value]);

    const onClickHideColumn = useCallback(() => {
        if (!column?.key) return;
        hideContextMenu();
        hideColumn(column.key);
    }, [column?.key, hideContextMenu, hideColumn]);

    if (!column) return <></>;

    return (
        <>
            <Menu>
                <Action
                    caption="Filter"
                    icon={<FilterIcon />}
                    disabled={!canBeFiltered}
                    onClick={onClickFilter}
                />
                <Action
                    caption="Hide"
                    icon={<HideIcon />}
                    onClick={onClickHideColumn}
                />
                {column.editable && (
                    <>
                        {isBoolean(column?.type) ? (
                            <>
                                <Action
                                    caption="Check Selected"
                                    icon={<CheckedIcon />}
                                    needsUpgrade={true}
                                />
                                <Action
                                    caption="Uncheck Selected"
                                    icon={<UncheckedIcon />}
                                    needsUpgrade={true}
                                />
                                <Action
                                    caption="Check All"
                                    icon={<CheckedIcon />}
                                    needsUpgrade={true}
                                />
                                <Action
                                    caption="Uncheck All"
                                    icon={<UncheckedIcon />}
                                    needsUpgrade={true}
                                />
                            </>
                        ) : (
                            <>
                                <Action
                                    caption="Edit Selected"
                                    icon={<EditIcon />}
                                    needsUpgrade={true}
                                />
                                <Action
                                    caption="EditAll"
                                    icon={<EditIcon />}
                                    needsUpgrade={true}
                                />
                            </>
                        )}
                    </>
                )}
                {column.editable && (
                    <Action
                        caption="Delete Column"
                        icon={<DeleteIcon />}
                        needsUpgrade={true}
                    />
                )}
                <Action
                    caption="Delete Row"
                    icon={<DeleteIcon />}
                    needsUpgrade={true}
                />
                <Action
                    caption="Duplicate Row"
                    icon={<AddIcon />}
                    needsUpgrade={true}
                />
            </Menu>
        </>
    );
};

export default CellContextMenu;

import Pill from '../../../components/ui/Pill';
import ToggleButton from '../../../components/ui/ToggleButton';
import { FunctionComponent, useCallback } from 'react';
import { Dataset, useDataset } from '../../../stores/dataset/dataset';
import tw from 'twin.macro';
import { TableView } from '../../../types';
import { useTableView } from '../context/tableViewContext';

const ButtonText = tw.span`align-middle text-sm leading-none`;

interface ViewButtonProps {
    activeTableView: TableView;
    onChangeTableView: (view: TableView) => void;
}

const fullRowCountSelector = (d: Dataset) => d.length;
const ViewAllButton: FunctionComponent<ViewButtonProps> = ({
    activeTableView,
    onChangeTableView,
}) => {
    const rowCount = useDataset(fullRowCountSelector);
    const handleOnChange = useCallback(
        () => onChangeTableView('full'),
        [onChangeTableView]
    );

    return (
        <ToggleButton
            data-test-tag="datagrid-all-tab-button"
            onChange={handleOnChange}
            checked={activeTableView === 'full'}
            size="medium"
            tooltip="Show all rows"
        >
            <ButtonText>All</ButtonText>{' '}
            <Pill data-test-tag="datagrid-all-count">{rowCount}</Pill>
        </ToggleButton>
    );
};

const filteredRowCountSelector = (d: Dataset) =>
    d.isIndexFiltered.filter((filtered) => filtered).length;
const ViewFilteredButton: FunctionComponent<ViewButtonProps> = ({
    activeTableView,
    onChangeTableView,
}) => {
    const rowCount = useDataset(filteredRowCountSelector);
    const handleOnChange = useCallback(
        () => onChangeTableView('filtered'),
        [onChangeTableView]
    );

    return (
        <ToggleButton
            data-test-tag="datagrid-filtered-tab-button"
            onChange={handleOnChange}
            checked={activeTableView === 'filtered'}
            size="medium"
            tooltip="Show filtered rows"
        >
            <ButtonText>Filtered</ButtonText>{' '}
            <Pill data-test-tag="datagrid-filtered-count">{rowCount}</Pill>
        </ToggleButton>
    );
};

const selectedRowCountSelector = (d: Dataset) =>
    d.isIndexSelected.filter((selected) => selected).length;
const ViewSelectedButton: FunctionComponent<ViewButtonProps> = ({
    activeTableView,
    onChangeTableView,
}) => {
    const rowCount = useDataset(selectedRowCountSelector);
    const handleOnChange = useCallback(
        () => onChangeTableView('selected'),
        [onChangeTableView]
    );

    return (
        <ToggleButton
            data-test-tag="datagrid-selected-tab-button"
            onChange={handleOnChange}
            checked={activeTableView === 'selected'}
            size="medium"
            tooltip="Show selected rows"
        >
            <ButtonText>Selected</ButtonText>{' '}
            <Pill data-test-tag="datagrid-selected-count">{rowCount}</Pill>
        </ToggleButton>
    );
};

const TableViewSelection: FunctionComponent = () => {
    const { tableView, setTableView } = useTableView();

    return (
        <>
            <ViewAllButton
                activeTableView={tableView}
                onChangeTableView={setTableView}
            />
            <ViewFilteredButton
                activeTableView={tableView}
                onChangeTableView={setTableView}
            />
            <ViewSelectedButton
                activeTableView={tableView}
                onChangeTableView={setTableView}
            />
        </>
    );
};

export default TableViewSelection;

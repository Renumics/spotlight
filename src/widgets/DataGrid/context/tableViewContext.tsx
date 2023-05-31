import * as React from 'react';
import { FunctionComponent, useContext } from 'react';
import { TableView } from '../../../types';

type RowContextState = {
    tableView: TableView;
    setTableView: (tableView: TableView) => void;
};

const RowContext = React.createContext<RowContextState>({
    tableView: 'full',
    setTableView: () => null,
});

export const TableViewProvider: FunctionComponent<
    RowContextState & {
        children: React.ReactNode;
    }
> = ({ children, ...props }) => {
    const { setTableView, tableView } = props;

    return (
        <RowContext.Provider value={{ setTableView, tableView }}>
            {children}
        </RowContext.Provider>
    );
};

export const useTableView = (): RowContextState => {
    return useContext(RowContext);
};

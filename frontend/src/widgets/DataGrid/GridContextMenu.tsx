import ContextMenu from '../../components/ui/ContextMenu';
import { FunctionComponent, MouseEvent, ReactNode, useCallback, useState } from 'react';
import tw from 'twin.macro';
import CellContextMenu from './Cell/CellContextMenu';
import HeaderCellContextMenu from './Cell/HeaderCellContextMenu';

const MenuWrapper = tw.div`
w-full h-full`;

type Props = {
    className?: string;
    children?: ReactNode;
};

const GridContextMenu: FunctionComponent<Props> = ({ className, children }) => {
    const [rowIndex, setRowIndex] = useState<number>(-1);
    const [columnIndex, setColumnIndex] = useState<number>(-1);

    const onContextMenu = useCallback((event: MouseEvent<HTMLElement>) => {
        const el = (event.target as HTMLElement).closest(
            'div[data-rowindex]'
        ) as HTMLElement;

        setColumnIndex(+(el?.dataset?.columnindex || -1));
        setRowIndex(+(el?.dataset?.rowindex || -1));
    }, []);

    return (
        <MenuWrapper onContextMenu={onContextMenu} className={className}>
            <ContextMenu
                content={
                    columnIndex >= 0 && rowIndex >= 0 ? (
                        <CellContextMenu
                            columnIndex={columnIndex}
                            rowIndex={rowIndex}
                        />
                    ) : (
                        columnIndex >= 0 && (
                            <HeaderCellContextMenu columnIndex={columnIndex} />
                        )
                    )
                }
            >
                <>{children}</>
            </ContextMenu>
        </MenuWrapper>
    );
};

export default GridContextMenu;

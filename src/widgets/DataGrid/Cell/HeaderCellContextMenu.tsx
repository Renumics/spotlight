import CopyIcon from '../../../icons/Copy';
import Button from '../../../components/ui/Button';
import { useContextMenu } from '../../../components/ui/ContextMenu';
import Menu from '../../../components/ui/Menu';
import { ComponentProps, FunctionComponent, useCallback } from 'react';
import 'twin.macro';
import { useColumn } from '../context/columnContext';
import { notify } from '../../../notify';

export interface Props {
    columnIndex: number;
}

interface ActionProps {
    caption: string;
    icon: JSX.Element;
    onClick?: ComponentProps<typeof Button>['onClick'];
}
const Action = ({ caption, icon, onClick }: ActionProps) => {
    return (
        <Menu.Item>
            <Button onClick={onClick}>
                {icon}
                <span tw="ml-1 font-normal">{caption}</span>
            </Button>
        </Menu.Item>
    );
};

const CellContextMenu: FunctionComponent<Props> = ({ columnIndex }) => {
    const column = useColumn(columnIndex);

    const { hide: hideContextMenu } = useContextMenu();

    const onClickCopyColumnName = useCallback(() => {
        navigator.clipboard
            .writeText(column.name)
            .then(() => notify('Column Name Copied to Clipboard'))
            .catch((error) => console.error(error));
        hideContextMenu();
    }, [column.name, hideContextMenu]);

    if (!column) return <></>;

    return (
        <>
            <Menu>
                <Action
                    caption="Copy Column Name"
                    icon={<CopyIcon />}
                    onClick={onClickCopyColumnName}
                />
            </Menu>
        </>
    );
};

export default CellContextMenu;

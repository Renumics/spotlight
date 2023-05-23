import { FunctionComponent, memo } from 'react';
import type { GridChildComponentProps as CellProps } from 'react-window';

type Props = CellProps;

const CellPlaceholder: FunctionComponent<Props> = ({ style }) => {
    return <div style={style}></div>;
};

export default memo(CellPlaceholder);

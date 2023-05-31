import { FunctionComponent } from 'react';
import type { GridChildComponentProps as CellProps } from 'react-window';
import tw from 'twin.macro';
import CellFactory from './CellFactory';

type Props = CellProps;

const StyledDiv = tw.div`
    whitespace-nowrap px-1 py-0.5 overflow-hidden text-sm border-b border-r w-full h-full
`;

const Cell: FunctionComponent<Props> = ({ style, columnIndex, rowIndex }) => {
    return (
        <StyledDiv
            style={style}
            data-columnindex={columnIndex}
            data-rowindex={rowIndex}
        >
            <CellFactory columnIndex={columnIndex} rowIndex={rowIndex} />
        </StyledDiv>
    );
};

export default Cell;

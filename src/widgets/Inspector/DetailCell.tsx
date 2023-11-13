import LensFactory from '../../systems/lenses/LensFactory';
import { FunctionComponent, memo, useCallback, useMemo } from 'react';
import { areEqual } from 'react-window';
import type { GridChildComponentProps as CellProps } from 'react-window';
import { Dataset, useDataset } from '../../stores/dataset';
import tw, { styled } from 'twin.macro';
import { shallow } from 'zustand/shallow';
import { useStore } from './store';

type Props = CellProps;

interface StyleProps {
    isRowHovered?: boolean;
}

const StyledDiv = styled.div(({ isRowHovered = false }: StyleProps) => [
    tw`transition-all duration-100 border-b border-r border-gray-400 bg-white overflow-hidden`,
    isRowHovered && tw`bg-gray-100`,
]);

const controlRowHighlightingSelector = (d: Dataset) => ({
    highlightRowAt: d.highlightRowAt,
    dehighlightRowAt: d.dehighlightRowAt,
});

const areEqualIgnoreScrollStart = (
    prevProps: Readonly<CellProps>,
    nextProps: Readonly<CellProps>
): boolean => {
    if (nextProps.isScrolling) {
        return areEqual(
            {
                ...prevProps,
                isScrolling: true,
            },
            { ...nextProps, isScrolling: true }
        );
    }
    return areEqual(prevProps, nextProps);
};

const columnsSelector = (d: Dataset) => d.columns;
const selectedIndicesSelector = (d: Dataset) => d.selectedIndices;

const Cell: FunctionComponent<Props> = ({
    style,
    isScrolling,
    columnIndex: dataRowIndex,
    rowIndex: dataColumnIndex,
}) => {
    const lenses = useStore((state) => state.lenses);
    const lensSpec = lenses[dataColumnIndex];
    const rowIndices = useDataset(selectedIndicesSelector);
    const allColumns = useDataset(columnsSelector);
    const columns = useMemo(
        () => allColumns.filter((c) => lensSpec.columns.includes(c.key)),
        [lensSpec, allColumns]
    );

    const originalIndex = rowIndices[dataRowIndex];

    const isHighlightedSelector = useCallback(
        (d: Dataset) => d.isIndexHighlighted[originalIndex],
        [originalIndex]
    );
    const { highlightRowAt, dehighlightRowAt } = useDataset(
        controlRowHighlightingSelector,
        shallow
    );

    const isRowHovered = useDataset(isHighlightedSelector);

    const onMouseEnter = useCallback(
        () => highlightRowAt(rowIndices[dataRowIndex]),
        [dataRowIndex, highlightRowAt, rowIndices]
    );
    const onMouseLeave = useCallback(
        () => dehighlightRowAt(rowIndices[dataRowIndex]),
        [dataRowIndex, dehighlightRowAt, rowIndices]
    );

    const changeLense = useStore((state) => state.changeLens);

    return (
        <StyledDiv
            style={style}
            isRowHovered={isRowHovered}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            {columns.length ? (
                <LensFactory
                    spec={lensSpec}
                    rowIndex={originalIndex}
                    columns={columns}
                    deferLoading={isScrolling}
                    onChange={changeLense}
                />
            ) : (
                <div>Columns Not Found</div>
            )}
        </StyledDiv>
    );
};

export default memo(Cell, areEqualIgnoreScrollStart);

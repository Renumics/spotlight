import Tag from '../../../components/ui/Tag';
import Tooltip from '../../../components/ui/Tooltip';
import { formatKind, useDataformat } from '../../../dataformat';
import { useColorTransferFunction } from '../../../hooks/useColorTransferFunction';
import * as React from 'react';
import { FunctionComponent, useCallback, useContext, useMemo } from 'react';
import { HiChevronDown, HiChevronUp } from 'react-icons/hi';
import type { GridChildComponentProps as CellProps } from 'react-window';
import { Dataset, Sorting, useDataset } from '../../../stores/dataset';
import tw from 'twin.macro';
import { useColumn } from '../context/columnContext';
import { useSortByColumn } from '../context/sortingContext';
import RelevanceIndicator from '../RelevanceIndicator';
import { ResizingContext } from '../context/resizeContext';
import ColumnBadge from '../../../components/ui/ColumnBadge';
import DataTypeIcon from '../../../components/DataTypeIcon';

interface SortingIndicatorProps {
    sorting?: Sorting;
}

const tagsSelector = (d: Dataset) => d.tags;

const SortingIndicator = React.memo(({ sorting }: SortingIndicatorProps) => {
    switch (sorting) {
        case 'ASC': {
            return <HiChevronUp tw="w-4 h-4" />;
        }
        case 'DESC': {
            return <HiChevronDown tw="w-4 h-4" />;
        }
        default: {
            return <></>;
        }
    }
});
SortingIndicator.displayName = 'SortingIndicator';

const stopPropagation: React.MouseEventHandler<HTMLButtonElement> = (event) => {
    event.preventDefault();
    event.stopPropagation();
};

type Props = CellProps;

const HeaderCell: FunctionComponent<Props> = ({ style, columnIndex }) => {
    const column = useColumn(columnIndex);
    const [columnSorting, sortBy, resetSorting] = useSortByColumn(column.key);

    const { startResizing, resizedIndex } = useContext(ResizingContext);

    const tags = useDataset(tagsSelector);
    const tagColorTransferFunction = useColorTransferFunction(tags, {
        kind: 'str',
        optional: true,
        lazy: true,
        binary: false,
    });

    const statsSelector = useCallback(
        (d: Dataset) => d.columnStats.full[column.key],
        [column.key]
    );
    const stats = useDataset(statsSelector);

    const onToggleSorting = useCallback(
        (event: React.MouseEvent<HTMLDivElement>) => {
            if (!event.ctrlKey) {
                resetSorting();
            }
            switch (columnSorting) {
                case 'ASC': {
                    sortBy('DESC');
                    return;
                }
                case 'DESC': {
                    sortBy();
                    return;
                }
                default: {
                    sortBy('ASC');
                }
            }
        },
        [columnSorting, resetSorting, sortBy]
    );

    const formatter = useDataformat();

    const tooltipContent = useMemo(
        () => (
            <div tw="flex flex-col max-w-xl">
                <div tw="font-bold break-all p-0.5">{column.name}</div>
                <div tw="flex flex-row justify-center">
                    <div tw="flex flex-row rounded-full bg-gray-300 text-xs space-x-1 px-2 py-0.5">
                        <DataTypeIcon type={column.type} />
                        <div>{formatKind(column.type.kind)}</div>
                    </div>
                </div>
                <div tw="text-gray-700 space-x-1.5 text-xs">
                    <span css={[!column.editable && tw`line-through`]}>editable</span>
                    <span css={[!column.optional && tw`line-through`]}>optional</span>
                </div>
                <div tw="flex flex-row flex-wrap justify-center w-full">
                    {column.tags?.map((tag) => (
                        <Tag
                            key={tag}
                            tag={tag}
                            color={tagColorTransferFunction(tag)}
                        />
                    ))}
                </div>
                {stats && (
                    <div tw="flex flex-row flex-wrap justify-center w-full">
                        <Tag tag={`min: ${formatter.format(stats.min, column.type)}`} />
                        <Tag tag={`max: ${formatter.format(stats.max, column.type)}`} />
                        <Tag
                            tag={`mean: ${formatter.format(stats.mean, {
                                kind: 'float',
                                optional: false,
                                lazy: false,
                                binary: false,
                            })}`}
                        />
                    </div>
                )}
                <div tw="flex-grow break-all flex">{column.description}</div>
            </div>
        ),
        [column, stats, tagColorTransferFunction, formatter]
    );

    const onStartResize: React.MouseEventHandler<HTMLButtonElement> = useCallback(
        (event) => {
            stopPropagation(event);
            startResizing(columnIndex);
        },
        [columnIndex, startResizing]
    );

    return (
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events,jsx-a11y/no-static-element-interactions
        <div
            tw="border-r-0 border-b pl-1 border-collapse border-solid border-gray-400 w-full h-full flex flex-row items-center"
            style={style}
            onClick={onToggleSorting}
            data-columnindex={columnIndex}
            data-rowindex={-1}
        >
            <div tw="flex flex-row flex-grow flex-shrink overflow-hidden">
                <Tooltip tw="overflow-hidden flex-shrink" content={tooltipContent}>
                    <ColumnBadge columnKey={column.key} />
                </Tooltip>
                <div tw="flex flex-grow items-center justify-end">
                    <RelevanceIndicator column={column} />
                    <SortingIndicator sorting={columnSorting} />
                </div>
            </div>
            <button
                onClick={stopPropagation}
                onMouseDown={onStartResize}
                css={[
                    tw`h-full w-[3px] border-r bg-none hover:border-r-0 hover:bg-gray-400 transition transform cursor-col-resize`,
                    resizedIndex.current === columnIndex && tw`bg-gray-400 border-r-0`,
                ]}
            />
        </div>
    );
};

export default HeaderCell;

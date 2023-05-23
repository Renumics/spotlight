import EditIcon from '../../../icons/Edit';
import Tag from '../../../components/ui/Tag';
import Tooltip from '../../../components/ui/Tooltip';
import dataformat from '../../../dataformat';
import { useColorTransferFunction } from '../../../hooks/useColorTransferFunction';
import * as React from 'react';
import { FunctionComponent, useCallback, useMemo } from 'react';
import { HiChevronDown, HiChevronUp } from 'react-icons/hi';
import type { GridChildComponentProps as CellProps } from 'react-window';
import { Dataset, Sorting, useDataset } from '../../../stores/dataset';
import tw from 'twin.macro';
import { useColumn } from '../context/columnContext';
import { useSortByColumn } from '../context/sortingContext';
import RelevanceIndicator from '../RelevanceIndicator';

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

type Props = CellProps;

const HeaderCell: FunctionComponent<Props> = ({ style, columnIndex }) => {
    const column = useColumn(columnIndex);
    const [columnSorting, sortBy, resetSorting] = useSortByColumn(column.key);

    const tags = useDataset(tagsSelector);
    const tagColorTransferFunction = useColorTransferFunction(tags, { kind: 'str' });

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

    const tooltipContent = useMemo(
        () => (
            <div tw="flex flex-col max-w-xl">
                <div tw="font-bold break-all">{column.name}</div>
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
                        <Tag
                            tag={`min: ${dataformat.format(stats.min, column.type)}`}
                        />
                        <Tag
                            tag={`max: ${dataformat.format(stats.max, column.type)}`}
                        />
                        <Tag
                            tag={`mean: ${dataformat.format(stats.mean, {
                                kind: 'float',
                            })}`}
                        />
                    </div>
                )}
                <div tw="flex-grow break-all flex">{column.description}</div>
            </div>
        ),
        [column, stats, tagColorTransferFunction]
    );

    return (
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events,jsx-a11y/no-static-element-interactions
        <div
            tw="border-r border-b px-1 border-collapse border-solid border-gray-400 w-full h-full flex flex-row overflow-hidden items-center"
            style={style}
            onClick={onToggleSorting}
        >
            <div tw="flex-grow flex-shrink truncate">
                <Tooltip tw="overflow-hidden w-full" content={tooltipContent}>
                    <div tw="truncate max-w-full block h-full self-center">
                        {column.editable && (
                            <EditIcon tw="text-gray-400 cursor-not-allowed" />
                        )}{' '}
                        {column.name}
                    </div>
                </Tooltip>
            </div>
            <div tw="flex items-center">
                <RelevanceIndicator column={column} />
                <SortingIndicator sorting={columnSorting} />
            </div>
        </div>
    );
};

export default HeaderCell;

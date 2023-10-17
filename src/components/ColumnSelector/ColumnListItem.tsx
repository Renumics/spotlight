import DataTypeIcon from '../DataTypeIcon';
import EditIcon from '../../icons/Edit';
import EditOffIcon from '../../icons/EditOff';
import Tag from '../ui/Tag';
import { useColorTransferFunction } from '../../hooks/useColorTransferFunction';
import * as React from 'react';
import { useCallback } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import tw from 'twin.macro';
import { DataColumn } from '../../types';

interface Props {
    column: DataColumn;
    selected: boolean;
    onChangeSelected?: (column: DataColumn, selected: boolean) => void;
}

const tagsSelector = (d: Dataset) => d.tags;

const ColumnListItem = ({ column, selected, onChangeSelected }: Props): JSX.Element => {
    const tags = useDataset(tagsSelector);
    const tagColorTransferFunction = useColorTransferFunction(tags, {
        kind: 'str',
        optional: true,
        binary: false,
        lazy: true,
    });

    const handleChange = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const isSelected = e.target.checked;
            onChangeSelected?.(column, isSelected);
        },
        [column, onChangeSelected]
    );

    return (
        <label tw="p-1 flex flex-row items-center hover:bg-gray-100 text-xs">
            <input
                type="checkbox"
                tw="hidden"
                onChange={handleChange}
                checked={selected}
            />
            <div tw="px-0.5 text-gray-600">
                <DataTypeIcon type={column.type} />
            </div>
            <div tw="px-0.5 text-gray-600">
                {column.editable ? <EditIcon /> : <EditOffIcon />}
            </div>
            <div
                css={[
                    selected && tw`font-bold`,
                    tw`px-1 flex-1 truncate min-w-[128px]`,
                ]}
            >
                {column.name}
            </div>
            <div tw="flex-initial overflow-hidden flex flex-row">
                {column.tags?.slice(0, 3).map((tag) => (
                    <Tag
                        key={tag}
                        tag={tag}
                        color={tagColorTransferFunction(tag)}
                        tw="flex-initial mx-0.5"
                    />
                ))}
                {column.tags && column.tags.length > 3 && (
                    <Tag tag={`+${column.tags.length - 3}`} tw="flex-initial mx-0.5" />
                )}
            </div>
        </label>
    );
};

export default ColumnListItem;

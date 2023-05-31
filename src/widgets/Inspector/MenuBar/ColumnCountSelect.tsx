import Select from '../../../components/ui/Select';
import Tooltip from '../../../components/ui/Tooltip';
import { FunctionComponent, ReactNode, useCallback } from 'react';
import { MdOutlineCalendarViewWeek } from 'react-icons/md';
import tw from 'twin.macro';

interface Props {
    visibleColumnsCount: number;
    setVisibleColumnsCount: (count: number) => void;
    visibleColumnsCountOptions: number[];
}

const ColumnCountIcon = tw(
    MdOutlineCalendarViewWeek
)`w-4 h-4 inline-block align-middle stroke-current`;

const singleValueTemplate = (children: ReactNode) => (
    <div tw="flex items-center">
        <ColumnCountIcon tw="mr-0.5" />
        <span>{children}</span>
    </div>
);

const ColumnCountSelect: FunctionComponent<Props> = ({
    visibleColumnsCount,
    setVisibleColumnsCount,
    visibleColumnsCountOptions,
}) => {
    const onChangeVisibleColumnsCount = useCallback(
        (value?: number) => {
            if (value) setVisibleColumnsCount(value);
        },
        [setVisibleColumnsCount]
    );

    return (
        <Tooltip content="Column Count">
            <Select
                isSearchable={false}
                options={visibleColumnsCountOptions}
                value={visibleColumnsCount}
                onChange={onChangeVisibleColumnsCount}
                variant="inline"
                singleValueTemplate={singleValueTemplate}
                // eslint-disable-next-line jsx-a11y/no-autofocus
                autoFocus={false}
            />
        </Tooltip>
    );
};

export default ColumnCountSelect;

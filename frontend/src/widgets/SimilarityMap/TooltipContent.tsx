import ColorIcon from '../../icons/Brush';
import LightbulbIcon from '../../icons/Lightbulb';
import LocationIcon from '../../icons/Location';
import SizeIcon from '../../icons/Resize';
import TableIcon from '../../icons/Table';
import ScalarValue from '../../components/ScalarValue';
import { FunctionComponent, ReactNode } from 'react';
import tw from 'twin.macro';
import { DataColumn, TableData } from '../../types';

const Entry = tw.div`flex flex-row items-center max-w-sm`;
const EntryLabel = tw.div`flex-grow pr-2 font-bold truncate text-left`;
const EntryValue = tw.div`whitespace-nowrap`;

interface SectionProps {
    icon: ReactNode;
    children?: ReactNode;
}

const Section: FunctionComponent<SectionProps> = ({ icon, children }) => {
    return (
        <div tw="flex flex-row border-b border-gray-300 last:border-b-0">
            <div tw="text-gray-700 border-r border-gray-300 px-1">{icon}</div>
            <div tw="flex-grow px-1">{children}</div>
        </div>
    );
};

interface DataSectionProps {
    rowIndex: number;
    data: TableData;
    columns: DataColumn[];
    icon: ReactNode;
    filter: boolean;
}

const DataSection: FunctionComponent<DataSectionProps> = ({
    rowIndex,
    data,
    columns,
    icon,
    filter,
}) => {
    return (
        <Section icon={icon} tw="border-t border-gray-300">
            {columns.map((column) => {
                const label = column.name;
                const value = data[column.key][rowIndex];

                return (
                    <Entry key={column.name}>
                        <EntryLabel>{label}</EntryLabel>
                        <EntryValue>
                            <ScalarValue
                                value={value}
                                column={column}
                                filtered={filter}
                            />
                        </EntryValue>
                    </Entry>
                );
            })}
        </Section>
    );
};

export interface Props {
    rowIndex: number;
    data: TableData;
    placementColumns: DataColumn[];
    colorColumn?: DataColumn;
    scaleColumn?: DataColumn;
    interestingColumns?: DataColumn[];
    filter: boolean;
}

const TooltipContent: FunctionComponent<Props> = ({
    rowIndex,
    data,
    placementColumns,
    colorColumn,
    scaleColumn,
    interestingColumns = [],
    filter,
}) => {
    return (
        <>
            <Section icon={<TableIcon />}>
                <Entry>
                    <EntryLabel>Row</EntryLabel>
                    <EntryValue>{rowIndex}</EntryValue>
                </Entry>
            </Section>
            <DataSection
                rowIndex={rowIndex}
                data={data}
                columns={placementColumns}
                icon={<LocationIcon />}
                filter={filter}
            />
            {colorColumn && (
                <DataSection
                    rowIndex={rowIndex}
                    data={data}
                    columns={[colorColumn]}
                    icon={<ColorIcon />}
                    filter={filter}
                />
            )}
            {scaleColumn && (
                <DataSection
                    rowIndex={rowIndex}
                    data={data}
                    columns={[scaleColumn]}
                    icon={<SizeIcon />}
                    filter={filter}
                />
            )}

            {interestingColumns.length > 0 && (
                <DataSection
                    rowIndex={rowIndex}
                    data={data}
                    columns={interestingColumns}
                    icon={<LightbulbIcon />}
                    filter={filter}
                />
            )}
        </>
    );
};

export default TooltipContent;

import UITooltip from '../../components/ui/Tooltip';
import { TransferFunction } from '../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { ReactNode, useMemo } from 'react';
import tw from 'twin.macro';
import { BinKey, HistogramData } from './types';
interface Props {
    xKey?: BinKey;
    yKey?: BinKey;
    histogramm: HistogramData;
    children?: ReactNode;
    transferFunction?: TransferFunction;
}

interface TooltipEntry {
    key: BinKey;
    allCount: number;
    filteredCount: number;
    color?: string;
    highlight?: boolean;
}

interface ContentProps {
    xEntry?: TooltipEntry;
    xColumnName?: string;
    yEntries: TooltipEntry[];
    yColumnName?: string;
}

const Entry = tw.li`flex flex-row items-center max-w-sm px-1 `;
const EntryLabel = tw.span`flex-grow pr-2 font-semibold truncate text-left`;
const EntryValue = tw.span`whitespace-nowrap`;
const EntryColorIndicator = tw.div`rounded-full mr-2`;

const TooltipContent = ({
    xEntry,
    xColumnName,
    yEntries = [],
    yColumnName = '',
}: ContentProps) => {
    if (xEntry === undefined || xColumnName === undefined) return <></>;
    return (
        <div tw="flex flex-row border-b border-gray-300 last:border-b-0">
            <ul tw="list-none">
                <Entry key="xColumnName" tw="mr-5">
                    <EntryLabel>{xColumnName}</EntryLabel>
                </Entry>
                <Entry key="xColumnCount" tw="pl-2 border-b border-gray-300">
                    <EntryLabel>{`${xEntry?.key}`}</EntryLabel>
                    <EntryValue>
                        {xEntry?.filteredCount}
                        {xEntry?.filteredCount !== xEntry?.allCount
                            ? `(${xEntry?.allCount})`
                            : ''}
                    </EntryValue>
                </Entry>
                {yColumnName && (
                    <>
                        <Entry key="yColumnName" tw="mr-5 mt-1">
                            <EntryLabel>{yColumnName}</EntryLabel>
                        </Entry>
                        {yEntries.map((e) => (
                            <Entry key={`yColumnCount-${e.key}`} tw="pl-2">
                                <EntryColorIndicator
                                    css={[
                                        tw`w-2 h-2`,
                                        e.color !== undefined &&
                                            `background-color: ${e.color}`,
                                    ]}
                                />
                                <EntryLabel>{`${e?.key}`}</EntryLabel>
                                <EntryValue>
                                    {e?.filteredCount}
                                    {e?.filteredCount !== e?.allCount
                                        ? `(${e?.allCount})`
                                        : ''}
                                </EntryValue>
                            </Entry>
                        ))}
                    </>
                )}
            </ul>
        </div>
    );
};

const Tooltip = ({
    xKey,
    yKey,
    histogramm,
    children,
    transferFunction,
}: Props): JSX.Element => {
    const { tooltipVisible, xEntry, yEntries } = useMemo(() => {
        if (
            xKey === undefined ||
            histogramm.all === undefined ||
            histogramm.filtered === undefined
        )
            return {
                tooltipVisible: false,
                xEntry: undefined,
                yEntries: [] as TooltipEntry[],
            };
        const allX = histogramm.all
            .map((s) => s.find((stack) => stack.xKey === xKey))
            .filter((s) => s !== undefined);

        const filteredX = histogramm.filtered
            .map((s) => s.find((stack) => stack.xKey === xKey))
            .filter((s) => s !== undefined);

        const values = allX
            .map((b, i): TooltipEntry | undefined => {
                const filteredBin = filteredX[i];
                if (b === undefined || filteredBin === undefined) return undefined;
                const allCount = isNaN(b[1]) ? 0 : b[1] - b[0];
                const filteredCount = isNaN(filteredBin[1])
                    ? 0
                    : filteredBin[1] - filteredBin[0];
                const key = b.yKey;
                return {
                    allCount,
                    filteredCount,
                    key,
                    highlight: key === yKey,
                    color: transferFunction
                        ? transferFunction(histogramm.yBins[b.yBin]?.value).css()
                        : undefined,
                };
            })
            .reverse()
            .filter((v) => v !== undefined);

        const summary: TooltipEntry = {
            allCount: _.sumBy(values, 'allCount'),
            filteredCount: _.sumBy(values, 'filteredCount'),
            key: xKey,
        };

        return {
            tooltipVisible: true,
            xEntry: summary,
            yEntries: values.filter((v) => v?.highlight) as TooltipEntry[],
        };
    }, [
        histogramm.all,
        histogramm.filtered,
        histogramm.yBins,
        transferFunction,
        xKey,
        yKey,
    ]);

    return (
        <UITooltip
            content={
                <TooltipContent
                    xEntry={xEntry}
                    yEntries={yEntries}
                    xColumnName={histogramm.xColumnName}
                    yColumnName={
                        histogramm.yBins.length > 0 ? histogramm.yColumnName : ''
                    }
                />
            }
            visible={tooltipVisible}
            followCursor={true}
            borderless={true}
            placement="auto-end"
        >
            {children}
        </UITooltip>
    );
};

export default Tooltip;

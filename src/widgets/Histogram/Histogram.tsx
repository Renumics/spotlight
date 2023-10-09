import FilterIcon from '../../icons/Filter';
import FilterOffIcon from '../../icons/FilterOff';
import SettingsIcon from '../../icons/Settings';
import Legend from '../../components/shared/Plot/Legend';
import Button from '../../components/ui/Button';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import {
    createConstantTransferFunction,
    createContinuousTransferFunction,
} from '../../hooks/useColorTransferFunction';
import useSize from '../../hooks/useSize';
import { useCallback, useMemo, useRef, useState } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';

import HistogramIcon from '../../icons/Histogram';
import tw from 'twin.macro';
import { Widget } from '../types';
import useWidgetConfig from '../useWidgetConfig';
import Bars from './Bars';
import Tooltip from './Tooltip';
import { BinKey } from './types';
import useHistogram from './useHistogram';
import XAxis from './XAxis';
import Info from '../../components/ui/Info';

const columnsSelector = (d: Dataset) => d.columns;

const validTypes = ['Category', 'str', 'bool', 'int', 'float'];
const defaultTypes = ['Category', 'bool', 'float'];

const Histogram: Widget = () => {
    const wrapper = useRef<HTMLDivElement>(null);

    const columns = useDataset(columnsSelector);
    const columnKeys = useMemo(
        () =>
            columns
                .filter((col) => !col.isInternal && validTypes.includes(col.type.kind))
                .map((col) => col.key),
        [columns]
    );
    const defaultColumnKey = useMemo(
        () =>
            columns
                .filter(
                    (col) => !col.isInternal && defaultTypes.includes(col.type.kind)
                )
                .map((col) => col.key)[0],
        [columns]
    );

    const [filter, setFilter] = useWidgetConfig('filter', false);

    const [_columnKey, setColumnKey] = useWidgetConfig<string | undefined>(
        'columnKey',
        defaultColumnKey
    );

    const columnKey =
        _columnKey && columnKeys.includes(_columnKey) ? _columnKey : undefined;

    const [_stackByColumnKey, setStackByColumnKey] = useWidgetConfig<
        string | undefined
    >('stackByColumnKey');

    const stackByColumnKey =
        _stackByColumnKey && columnKeys.includes(_stackByColumnKey)
            ? _stackByColumnKey
            : undefined;

    const { width, height } = useSize(wrapper);

    const histogram = useHistogram(columnKey, stackByColumnKey);

    const [hoveredBucket, setHoveredBucket] = useState<{
        xKey?: BinKey;
        yKey?: BinKey;
    }>();

    const columnColorTransferFunctionSelector = useCallback(
        (d: Dataset) =>
            stackByColumnKey
                ? d.colorTransferFunctions[stackByColumnKey]?.[
                      filter ? 'filtered' : 'full'
                  ][0]
                : createConstantTransferFunction(),
        [filter, stackByColumnKey]
    );

    const columnColorTransferFunction = useDataset(columnColorTransferFunctionSelector);

    const transferFunction = useMemo(() => {
        if (columnColorTransferFunction.kind !== 'continuous')
            return columnColorTransferFunction;
        // if tf is continuous a new scale has to be generated with class breaks

        const [min, max] = columnColorTransferFunction.domain;
        return createContinuousTransferFunction(
            min,
            max,
            columnColorTransferFunction.dType,
            [histogram.yBins[0].min, ...histogram.yBins.map(({ max }) => max)]
        );
    }, [columnColorTransferFunction, histogram.yBins]);

    const toggleHideUnfiltered = () => setFilter((state) => !state);

    return (
        <div tw="flex flex-col w-full h-full items-stretch justify-center">
            <div tw="flex flex-row bg-gray-100 border-b border-gray-400 items-center">
                <div tw="flex-grow text-xs px-2 py-0.5 font-bold">{columnKey}</div>
                <Button
                    onClick={toggleHideUnfiltered}
                    tooltip={filter ? 'show unfiltered' : 'hide unfiltered'}
                >
                    {filter ? <FilterOffIcon /> : <FilterIcon />}
                </Button>
                <Dropdown
                    content={
                        <Menu tw="w-64">
                            <Menu.ColumnSelect
                                title="Column"
                                selectableColumns={columnKeys}
                                selected={columnKey}
                                onChangeColumn={setColumnKey}
                            />
                            <Menu.ColumnSelect
                                title="Stack by Column"
                                selectableColumns={columnKeys}
                                selected={stackByColumnKey}
                                onChangeColumn={setStackByColumnKey}
                            />
                        </Menu>
                    }
                    tooltip="Settings"
                >
                    <SettingsIcon />
                </Dropdown>
            </div>
            <div tw="flex-grow overflow-hidden mt-1.5" ref={wrapper}>
                {histogram.xBins.length > 0 ? (
                    <Tooltip
                        histogramm={histogram}
                        xKey={hoveredBucket?.xKey}
                        yKey={hoveredBucket?.yKey}
                        transferFunction={transferFunction}
                    >
                        <svg
                            css={[histogram.xBins.length === 0 && tw`hidden`]}
                            width={width}
                            height={height}
                            viewBox={`0 0 ${width} ${height}`}
                        >
                            <Bars
                                width={width}
                                height={height}
                                transferFunction={transferFunction}
                                histogram={histogram}
                                hideUnfiltered={filter}
                                onHoverBin={setHoveredBucket}
                            />

                            <XAxis
                                width={width}
                                height={height}
                                histogram={histogram}
                                hideUnfiltered={filter}
                            />
                        </svg>
                    </Tooltip>
                ) : (
                    <Info>No column selected.</Info>
                )}
            </div>
            {histogram.yColumnName && histogram.yBins.length > 0 && (
                <Legend
                    tw="top-2.5 flex flex-row items-end max-w-[none] w-full justify-start"
                    transferFunction={transferFunction}
                    caption={stackByColumnKey || ''}
                />
            )}
        </div>
    );
};

Histogram.defaultName = 'Histogram';
Histogram.icon = HistogramIcon;
Histogram.key = 'histogram';

export default Histogram;

import ScatterPlotIcon from '../../icons/ScatterPlot';
import Plot, {
    MergeStrategy,
    Points,
    Zoom,
    ZoomHandle,
} from '../../components/shared/Plot';
import Brush from '../../components/shared/Plot/Brush';
import Legend from '../../components/shared/Plot/Legend';
import Tooltip from '../../components/shared/Plot/Tooltip';
import XAxis from '../../components/shared/Plot/XAxis';
import YAxis from '../../components/shared/Plot/YAxis';
import TooltipContent from '../../widgets/SimilarityMap/TooltipContent';
import { DataType } from '../../datatypes';
import { createConstantTransferFunction } from '../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { useCallback, useMemo, useRef } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import tw, { styled } from 'twin.macro';
import {
    ColumnsStats,
    DataColumn,
    DataStatistics,
    isNumberColumn,
    NumberColumn,
    TableData,
} from '../../types';
import { createSizeTransferFunction } from '../../dataformat';
import { shallow } from 'zustand/shallow';
import { Widget } from '../types';
import useWidgetConfig from '../useWidgetConfig';
import MenuBar from './MenuBar';
import Info from '../../components/ui/Info';

const ScatterplotViewContainer = styled.div`
    ${tw`bg-gray-100 border-gray-400 w-full h-full overflow-hidden`}
`;

const StyledLegend = styled(Legend)`
    ${tw`w-1/4 mt-10`}
`;

const PlotContainer = tw.div`flex top-0 left-0 w-full h-full`;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function calculateZScore(value: any, stats?: DataStatistics) {
    if (isNaN(value) || stats === undefined) {
        return 0;
    }
    return Math.abs(value - stats.mean) / stats.std;
}

function sortColumnsByZScore(
    rowIndex: number,
    data: TableData,
    columns: DataColumn[],
    stats: ColumnsStats
) {
    return [...columns].sort((a, b) => {
        return (
            calculateZScore(data[b.key][rowIndex], stats[b.key]) -
            calculateZScore(data[a.key][rowIndex], stats[a.key])
        );
    });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function convertValueToPosition(value: any, type: DataType) {
    if (type.kind === 'bool') return value ? 1 : 0;
    if (isNaN(value)) return 0;
    return value;
}

const datasetSelector = (d: Dataset) => ({
    allIndices: d.indices,
    columnData: d.columnData,
    isIndexFiltered: d.isIndexFiltered,
    filteredIndices: d.filteredIndices,
    isIndexSelected: d.isIndexSelected,
    selectedIndices: d.selectedIndices,
    isIndexHighlighted: d.isIndexHighlighted,
    highlightRowAt: d.highlightRowAt,
    dehighlightAll: d.dehighlightAll,
    selectRows: d.selectRows,
});

const allColumnsByKeySelector = (d: Dataset) =>
    d.columns.reduce((a: { [key: string]: DataColumn }, b) => {
        a[b.key] = b;
        return a;
    }, {});

const columnStatsSelector = (d: Dataset) => d.columnStats;

const ScatterplotView: Widget = () => {
    const scatterPlotRef = useRef<ZoomHandle>(null);

    const [xAxisColumnKey, setXAxisColumnKey] = useWidgetConfig<string>(
        'xAxisColumn',
        ''
    );
    const [yAxisColumnKey, setYAxisColumnKey] = useWidgetConfig<string>(
        'yAxisColumn',
        ''
    );
    const [colorByKey, setColorByKey] = useWidgetConfig<string>('colorBy', '');
    const [sizeByKey, setSizeByKey] = useWidgetConfig<string>('sizeBy', '');
    const [filter, setFilter] = useWidgetConfig<boolean>('filter', false);

    const columnStatsAll = useDataset(columnStatsSelector);

    const columnStats = filter ? columnStatsAll.filtered : columnStatsAll.full;

    const {
        allIndices,
        columnData,
        isIndexFiltered,
        filteredIndices,
        isIndexSelected,
        isIndexHighlighted,
        selectRows,
        highlightRowAt,
        dehighlightAll,
    } = useDataset(datasetSelector, shallow);

    const allColumns = useDataset(allColumnsByKeySelector, shallow);
    const visibleIndices = useMemo(() => {
        if (filter) {
            return filteredIndices;
        }
        return allIndices;
    }, [filter, filteredIndices, allIndices]);

    const hasEnoughRows = visibleIndices.length > 0;

    const colorBy = allColumns[colorByKey];
    const colorByData = columnData[colorByKey];

    const transferFunctionSelector = useCallback(
        (d: Dataset) =>
            colorByKey !== undefined && colorByKey.length > 0
                ? d.colorTransferFunctions[colorByKey]?.[filter ? 'filtered' : 'full']
                : createConstantTransferFunction(),
        [colorByKey, filter]
    );

    const transferFunction = useDataset(transferFunctionSelector);

    const colors = useMemo(() => {
        const colors: string[] = new Array(visibleIndices.length);
        visibleIndices.forEach((index, i) => {
            colors[i] = transferFunction?.(colorByData?.[index]).hex();
        });
        return colors;
    }, [visibleIndices, colorByData, transferFunction]);

    const sizeByColumn = allColumns[sizeByKey];
    const sizeByData = columnData[sizeByKey];
    const sizeTrans = useMemo(
        () => createSizeTransferFunction(sizeByColumn, sizeByData, visibleIndices),
        [sizeByColumn, sizeByData, visibleIndices]
    );

    const sizes = useMemo(() => {
        const sizes = new Array(visibleIndices.length);
        visibleIndices.forEach(
            (index, i) => (sizes[i] = sizeTrans(sizeByData ? sizeByData[index] : 0))
        );
        return sizes;
    }, [visibleIndices, sizeTrans, sizeByData]);

    const xColumn = allColumns[xAxisColumnKey];
    const xData = columnData[xAxisColumnKey];
    const yColumn = allColumns[yAxisColumnKey];
    const yData = columnData[yAxisColumnKey];

    const positions: [number, number][] = useMemo(() => {
        if (xColumn === undefined || yColumn === undefined) return [];

        const positions: [number, number][] = new Array(visibleIndices.length);
        visibleIndices.forEach((index, i) => {
            const x = xData[index] ?? 0;
            const y = yData[index] ?? 0;
            positions[i] = [
                convertValueToPosition(x, xColumn.type),
                convertValueToPosition(y, yColumn.type),
            ];
        });
        return positions;
    }, [visibleIndices, xColumn, yColumn, xData, yData]);

    const selected = useMemo(() => {
        const selected = new Array(visibleIndices.length);
        visibleIndices.forEach((index, i) => {
            selected[i] = isIndexSelected[index];
        });
        return selected;
    }, [isIndexSelected, visibleIndices]);

    const hidden = useMemo(() => {
        const hidden = new Array(visibleIndices.length);
        visibleIndices.forEach((index, i) => {
            hidden[i] = !isIndexFiltered[index];
        });
        return hidden;
    }, [isIndexFiltered, visibleIndices]);

    const getOriginalIndices = useCallback(
        (indices: number[]) => indices.map((index) => visibleIndices[index]),
        [visibleIndices]
    );

    const setHighlightedPoint = useCallback(
        (index: number | undefined) => {
            if (index !== undefined) {
                highlightRowAt(visibleIndices[index], true);
            } else {
                dehighlightAll();
            }
        },
        [highlightRowAt, dehighlightAll, visibleIndices]
    );
    const isPointHighlighted = useCallback(
        (index: number) => isIndexHighlighted[visibleIndices[index]] ?? false,
        [isIndexHighlighted, visibleIndices]
    );

    const handleSelect = useCallback(
        (indices: number[], mergeStrategy: MergeStrategy) => {
            const newRowIndices = getOriginalIndices(indices);
            switch (mergeStrategy) {
                case 'replace':
                    selectRows(newRowIndices);
                    break;
                case 'union':
                    selectRows((currentSelection) =>
                        _.union(currentSelection, newRowIndices)
                    );
                    break;
                case 'difference':
                    selectRows((currentSelection) =>
                        _.difference(currentSelection, newRowIndices)
                    );
                    break;
                case 'intersect':
                    selectRows((currentSelection) =>
                        _.intersection(currentSelection, newRowIndices)
                    );
                    break;
                default:
                    throw new Error(`${mergeStrategy} not in type MergeStrategy`);
            }
        },
        [getOriginalIndices, selectRows]
    );

    const handleClick = useCallback(
        (key?: number, mergeMode: MergeStrategy = 'replace') => {
            if (key === undefined) {
                handleSelect([], mergeMode);
            } else {
                handleSelect([key], mergeMode);
            }
        },
        [handleSelect]
    );

    const handleReset = useCallback(() => {
        scatterPlotRef.current?.reset();
    }, []);

    const getTooltip = useCallback(
        (index?: number) => {
            const placeByColumns: string[] = [];
            if (xAxisColumnKey) placeByColumns.push(xAxisColumnKey);
            if (yAxisColumnKey && yAxisColumnKey !== xAxisColumnKey)
                placeByColumns.push(yAxisColumnKey);
            const maxInterestingColumns = 3;
            const rowIndex = index !== undefined && getOriginalIndices([index])[0];
            if (!rowIndex) return;

            const defaultColumns = _.compact(
                _.union(placeByColumns, [colorByKey, sizeByKey])
            );

            // compute z-scores for all number columns and order them descending
            const remainingColumns = Object.values(allColumns).filter(
                (col) => isNumberColumn(col) && !defaultColumns.includes(col.key)
            ) as NumberColumn[];
            const interestingColumns = sortColumnsByZScore(
                rowIndex,
                columnData,
                remainingColumns,
                columnStats
            ).slice(0, maxInterestingColumns);

            return (
                <TooltipContent
                    rowIndex={rowIndex}
                    data={columnData}
                    placementColumns={placeByColumns.map((key) => allColumns[key])}
                    colorColumn={allColumns[colorByKey]}
                    scaleColumn={allColumns[sizeByKey]}
                    interestingColumns={interestingColumns}
                    filter={filter}
                />
            );
        },
        [
            xAxisColumnKey,
            yAxisColumnKey,
            getOriginalIndices,
            colorByKey,
            sizeByKey,
            allColumns,
            columnData,
            columnStats,
            filter,
        ]
    );

    const placeableColumns = useMemo(
        () =>
            Object.values(allColumns)
                .filter((col) => ['int', 'float', 'bool'].includes(col.type.kind))
                .map((col) => col.key),
        [allColumns]
    );
    const colorableColumns = useMemo(
        () =>
            Object.values(allColumns)
                .filter((col) =>
                    ['int', 'float', 'str', 'bool', 'Category'].includes(col.type.kind)
                )
                .map((col) => col.key),
        [allColumns]
    );
    const scaleableColumns = useMemo(
        () =>
            Object.values(allColumns)
                .filter((col: DataColumn) =>
                    ['int', 'float', 'bool'].includes(col.type.kind)
                )
                .map((col) => col.key),
        [allColumns]
    );

    const areColumnsSelected =
        placeableColumns.includes(xAxisColumnKey) &&
        placeableColumns.includes(yAxisColumnKey);

    return (
        <ScatterplotViewContainer>
            {!areColumnsSelected && (
                <Info>
                    <span>Select columns to display on the x- and y-axis.</span>
                </Info>
            )}
            {areColumnsSelected && !hasEnoughRows && (
                <Info>
                    <span>Not enough rows</span>
                </Info>
            )}
            {areColumnsSelected && hasEnoughRows && (
                <PlotContainer>
                    <Plot
                        points={positions}
                        isPointHighlighted={isPointHighlighted}
                        setHighlightedPoint={setHighlightedPoint}
                    >
                        <Zoom ref={scatterPlotRef} />
                        <Points
                            colors={colors}
                            sizes={sizes}
                            hidden={hidden}
                            selected={selected}
                            onClick={handleClick}
                        />
                        <Tooltip content={getTooltip} />
                        <Brush hidden={hidden} onSelect={handleSelect} />
                        <XAxis caption={xAxisColumnKey} />
                        <YAxis caption={yAxisColumnKey} />
                    </Plot>

                    {colorByKey && (
                        <StyledLegend
                            transferFunction={transferFunction}
                            caption={colorBy.name || colorByKey}
                            align="right"
                            arrange="vertical"
                        />
                    )}
                </PlotContainer>
            )}
            <MenuBar
                colorBy={colorByKey}
                sizeBy={sizeByKey}
                xAxisColumn={xAxisColumnKey}
                yAxisColumn={yAxisColumnKey}
                filter={filter || false}
                placeableColumns={placeableColumns}
                colorableColumns={colorableColumns}
                scaleableColumns={scaleableColumns}
                onChangeXAxisColumn={setXAxisColumnKey}
                onChangeYAxisColumn={setYAxisColumnKey}
                onChangeColorBy={setColorByKey}
                onChangeSizeBy={setSizeByKey}
                onChangeFilter={setFilter}
                onReset={handleReset}
            />
        </ScatterplotViewContainer>
    );
};

ScatterplotView.defaultName = 'Scatter Plot';
ScatterplotView.icon = ScatterPlotIcon;
ScatterplotView.key = 'scatterplot';

export default ScatterplotView;

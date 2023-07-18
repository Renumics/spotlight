import SimilaritiesIcon from '../../icons/Bubbles';
import LoadingIndicator from '../../components/LoadingIndicator';
import Plot, {
    MergeStrategy,
    Points,
    Zoom,
    ZoomHandle,
} from '../../components/shared/Plot';
import Brush from '../../components/shared/Plot/Brush';
import Legend from '../../components/shared/Plot/Legend';
import Tooltip from '../../components/shared/Plot/Tooltip';
import { Hint } from '../../components/ui/Menu/MultiColumnSelect';
import { createConstantTransferFunction } from '../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import dataService, { PCANormalization, UmapMetric } from '../../services/data';
import shallowequal from 'shallowequal';
import { Dataset, useDataset } from '../../stores/dataset';
import tw, { styled } from 'twin.macro';
import {
    ColumnsStats,
    DataColumn,
    DataStatistics,
    IndexArray,
    isEmbeddingColumn,
    isNumberColumn,
    NumberColumn,
    TableData,
} from '../../types';
import { createSizeTransferFunction } from '../../dataformat';
import { v4 as uuidv4 } from 'uuid';
import { shallow } from 'zustand/shallow';
import { Widget } from '../types';
import useWidgetConfig from '../useWidgetConfig';
import MenuBar from './MenuBar';
import TooltipContent from './TooltipContent';
import { ReductionMethod } from './types';
import Info from '../../components/ui/Info';

const MapContainer = styled.div`
    ${tw`bg-gray-100 border-gray-400 w-full h-full overflow-hidden`}
`;

const PlotContainer = tw.div`top-0 left-0 w-full h-full`;

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

const datasetSelector = (d: Dataset) => ({
    fullColumns: d.columns,
    columnData: d.columnData,
    allIndices: d.indices,
    isIndexFiltered: d.isIndexFiltered,
    filteredIndices: d.filteredIndices,
    isIndexSelected: d.isIndexSelected,
    selectedIndices: d.selectedIndices,
    isIndexHighlighted: d.isIndexHighlighted,
    highlightRowAt: d.highlightRowAt,
    dehighlightAll: d.dehighlightAll,
    selectRows: d.selectRows,
});

const columnStatsSelector = (d: Dataset) => d.columnStats;

const SimilarityMap: Widget = () => {
    const scatterPlotRef = useRef<ZoomHandle>(null);
    const [storedPlaceByColumnKeys, setStoredPlaceByColumnKeys] =
        useWidgetConfig<string[]>('placeBy');

    const [filter, setFilter] = useWidgetConfig('filter', false);
    const [storedColorByKey, setStoredColorByKey] = useWidgetConfig<string>('colorBy');
    const [sizeByKey, setSizeByKey] = useWidgetConfig<string>('sizeBy');
    const [reductionMethod, setReductionMethod] = useWidgetConfig<
        ReductionMethod | undefined
    >('reductionMethod', 'umap');
    const [umapNNeighbors, setUmapNNeighbors] = useWidgetConfig('umapNNeighbors', 20);
    const [umapMetric, setUmapMetric] = useWidgetConfig<UmapMetric | undefined>(
        'umapMetric',
        'euclidean'
    );
    const [umapMinDist, setUmapMinDist] = useWidgetConfig('umapMinDist', 0.15);
    const [pcaNormalization, setPCANormalization] = useWidgetConfig<
        PCANormalization | undefined
    >('pcaNormalization', 'none');

    const [isComputing, setIsComputing] = useState(false);

    const {
        fullColumns,
        columnData,
        allIndices,
        filteredIndices,
        selectedIndices,
        selectRows,
        isIndexHighlighted,
        highlightRowAt,
        dehighlightAll,
    } = useDataset(datasetSelector, shallow);

    const columnStatsAll = useDataset(columnStatsSelector);

    const columnStats = filter ? columnStatsAll.filtered : columnStatsAll.full;

    const colorByKey = useMemo(() => {
        if (!fullColumns.length) {
            return undefined;
        }
        const availableColumns = fullColumns
            .filter((col) => !col.isInternal)
            .filter((col) =>
                ['int', 'float', 'str', 'bool', 'Category'].includes(col.type.kind)
            )
            .sort((c1, c2) => c1.order - c2.order)
            .map((c) => c.key);

        if (storedColorByKey && availableColumns.includes(storedColorByKey)) {
            return storedColorByKey;
        }
        return availableColumns[0];
    }, [fullColumns, storedColorByKey]);

    const colorBySelector = useCallback(
        (d: Dataset) => d.columns.find((c) => c.key === colorByKey),
        [colorByKey]
    );
    const colorBy = useDataset(colorBySelector);
    const colorByData = useMemo(
        () => (colorByKey ? columnData[colorByKey] : []),
        [colorByKey, columnData]
    );

    const sizeBySelector = useCallback(
        (d: Dataset) => d.columns.find((c) => c.key === sizeByKey),
        [sizeByKey]
    );
    const sizeBy = useDataset(sizeBySelector);
    const sizeByData = useMemo(
        () => (sizeByKey ? columnData[sizeByKey] : []),
        [sizeByKey, columnData]
    );

    const indices = useMemo(() => {
        if (filter) {
            return filteredIndices;
        }
        return allIndices;
    }, [filter, filteredIndices, allIndices]);

    const embeddableColumnKeys = useMemo(() => {
        return fullColumns
            .filter(
                (col) =>
                    ['int', 'bool', 'float', 'Category', 'Embedding'].includes(
                        col.type.kind
                    ) && !col.isInternal
            )
            .map((c) => c.key);
    }, [fullColumns]);

    const embeddableColumnsSelector = useCallback(
        (d: Dataset) => d.columns.filter((c) => embeddableColumnKeys.includes(c.key)),
        [embeddableColumnKeys]
    );
    const embeddableColumns = useDataset(embeddableColumnsSelector, shallow);
    const embeddableColumnsHints = useMemo(() => {
        const hints: Record<string, Hint> = {};
        embeddableColumns.forEach((column) => {
            if (isEmbeddingColumn(column) && column.type.embeddingLength > 512) {
                hints[column.key] = {
                    type: 'warning',
                    message: (
                        <>
                            Embedding length is {'>'} 512 ({column.type.embeddingLength}
                            ) which might
                            <br />
                            <b>negatively influence performance</b>.
                            <br />
                            Consider reducing it.
                        </>
                    ),
                };
            }
        });
        return hints;
    }, [embeddableColumns]);

    const placeByColumnKeys = useMemo(() => {
        // When there is no stored selection, select the first available embedding
        if (storedPlaceByColumnKeys === undefined) {
            const firstEmbedding = fullColumns.find(
                (col) => col.type.kind === 'Embedding'
            );
            if (firstEmbedding) {
                return [firstEmbedding.name];
            } else {
                return [];
            }
        }

        // When the user's data changes keep the selected embedding column
        // or try to select a sensible column if the selected column doesn't exist
        // in the new datatable
        const matchingColumns = _.intersection(
            storedPlaceByColumnKeys,
            embeddableColumnKeys
        );

        if (
            shallowequal(storedPlaceByColumnKeys, matchingColumns) &&
            storedPlaceByColumnKeys?.length !== 0
        ) {
            return storedPlaceByColumnKeys;
        }

        // Return the previous array if it was empty
        // to prevent unnecessary state updates
        if (!storedPlaceByColumnKeys?.length) {
            return storedPlaceByColumnKeys;
        }

        // If everything else fails return an empty array.
        return [];
    }, [fullColumns, embeddableColumnKeys, storedPlaceByColumnKeys]);

    const placeByColumnsSelector = useCallback(
        (d: Dataset) => d.columns.filter((c) => placeByColumnKeys.includes(c.key)),
        [placeByColumnKeys]
    );
    const placeByColumns = useDataset(placeByColumnsSelector, shallow);

    const [positions, setPositions] = useState<[number, number][]>([]);

    const [visibleIndices, setVisibleIndices] = useState<IndexArray>([]);

    const selected = useMemo(() => {
        const selected: boolean[] = [];
        visibleIndices.forEach((index, i) => {
            selected[i] = selectedIndices.includes(index);
        });
        return selected;
    }, [selectedIndices, visibleIndices]);

    const hidden = useMemo(() => {
        const hidden: boolean[] = [];
        visibleIndices.forEach((index, i) => {
            hidden[i] = !filteredIndices.includes(index);
        });
        return hidden;
    }, [visibleIndices, filteredIndices]);

    const transferFunctionSelector = useCallback(
        (d: Dataset) =>
            colorByKey !== undefined && colorByKey.length > 0
                ? d.colorTransferFunctions[colorByKey]?.[
                      filter ? 'filtered' : 'full'
                  ][0]
                : createConstantTransferFunction(
                      colorBy?.type || {
                          kind: 'Unknown',
                          optional: false,
                          binary: false,
                      }
                  ),
        [colorByKey, filter, colorBy?.type]
    );

    const transferFunction = useDataset(transferFunctionSelector);

    const colors = useMemo(() => {
        const colors: string[] = new Array(visibleIndices.length);
        visibleIndices.forEach((index, i) => {
            colors[i] = transferFunction?.(colorByData?.[index]).hex();
        });
        return colors;
    }, [visibleIndices, colorByData, transferFunction]);

    const sizeTrans = useMemo(
        () => createSizeTransferFunction(sizeBy, sizeByData, visibleIndices),
        [sizeBy, visibleIndices, sizeByData]
    );

    const sizes = useMemo(() => {
        const sizes = new Array(visibleIndices.length);
        visibleIndices.forEach((index, i) => {
            sizes[i] = sizeTrans(sizeByData?.[index] ?? 0);
        });
        return sizes;
    }, [visibleIndices, sizeByData, sizeTrans]);

    const widgetId = useMemo(() => uuidv4(), []);

    useEffect(() => {
        if (!indices.length || !placeByColumnKeys.length) {
            setVisibleIndices([]);
            setPositions([]);
            setIsComputing(false);
            return;
        }

        setIsComputing(true);

        const reductionPromise =
            reductionMethod === 'umap'
                ? dataService.computeUmap(
                      widgetId,
                      placeByColumnKeys,
                      indices,
                      umapNNeighbors,
                      umapMetric ?? 'euclidean',
                      umapMinDist
                  )
                : dataService.computePCA(
                      widgetId,
                      placeByColumnKeys,
                      indices,
                      pcaNormalization ?? 'none'
                  );

        let cancelled = false;
        reductionPromise.then(({ points, indices }) => {
            if (cancelled) return;
            setVisibleIndices(indices);
            setPositions(points);
            setIsComputing(false);
        });

        return () => {
            cancelled = true;
        };
    }, [
        widgetId,
        placeByColumnKeys,
        indices,
        reductionMethod,
        umapNNeighbors,
        umapMetric,
        umapMinDist,
        pcaNormalization,
    ]);

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

    const getTooltip = useCallback(
        (index?: number) => {
            const maxInterestingColumns = 3;
            const rowIndex = index !== undefined && getOriginalIndices([index])[0];
            if (!rowIndex) return;

            const defaultColumns = _.compact(
                _.union(placeByColumns, [colorBy, sizeBy])
            );

            // compute z-scores for all number columns and order them descending
            //
            const remainingColumns = fullColumns.filter(
                (col) =>
                    isNumberColumn(col) &&
                    !col.isInternal &&
                    !defaultColumns.includes(col)
            ) as NumberColumn[];
            const interestingColumns = sortColumnsByZScore(
                rowIndex,
                columnData,
                remainingColumns,
                columnStats
            ).slice(0, maxInterestingColumns);

            const placementColumnsByZScore = sortColumnsByZScore(
                rowIndex,
                columnData,
                placeByColumns,
                columnStats
            );

            return (
                <TooltipContent
                    rowIndex={rowIndex}
                    data={columnData}
                    placementColumns={placementColumnsByZScore}
                    colorColumn={colorBy}
                    scaleColumn={sizeBy}
                    interestingColumns={interestingColumns}
                    filter={filter}
                />
            );
        },
        [
            getOriginalIndices,
            placeByColumns,
            colorBy,
            sizeBy,
            fullColumns,
            columnData,
            columnStats,
            filter,
        ]
    );

    const handleSelect = useCallback(
        (indices: number[], mergeStrategy: MergeStrategy) => {
            const newIndices = getOriginalIndices(indices);
            switch (mergeStrategy) {
                case 'replace':
                    selectRows(newIndices);
                    break;
                case 'union':
                    selectRows((currentSelection) =>
                        _.union(currentSelection, newIndices)
                    );
                    break;
                case 'difference':
                    selectRows((currentSelection) =>
                        _.difference(currentSelection, newIndices)
                    );
                    break;
                case 'intersect':
                    selectRows((currentSelection) =>
                        _.intersection(currentSelection, newIndices)
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

    const resetPlot = useCallback(() => {
        scatterPlotRef.current?.reset();
    }, []);

    const areColumnsSelected = !!placeByColumnKeys.length;
    const hasVisibleRows = !!visibleIndices.length;

    return (
        <MapContainer data-test-tag="similaritymap">
            {isComputing && <LoadingIndicator />}
            {!areColumnsSelected && !isComputing && (
                <Info>
                    <span>
                        Select columns and show at least two rows to display similarity
                        map
                    </span>
                </Info>
            )}
            {areColumnsSelected && !hasVisibleRows && !isComputing && (
                <Info>
                    <span>Not enough rows</span>
                </Info>
            )}
            {areColumnsSelected && hasVisibleRows && !isComputing && (
                <PlotContainer>
                    <Plot
                        points={positions}
                        isPointHighlighted={isPointHighlighted}
                        setHighlightedPoint={setHighlightedPoint}
                        scaleUniform={true}
                    >
                        <Zoom ref={scatterPlotRef} />
                        <Points
                            colors={colors}
                            sizes={sizes}
                            selected={selected}
                            hidden={hidden}
                            onClick={handleClick}
                        />
                        <Tooltip content={getTooltip} />
                        <Brush hidden={hidden} onSelect={handleSelect} />
                    </Plot>
                    {colorByKey && (
                        <Legend
                            transferFunction={transferFunction}
                            caption={colorBy?.name || colorByKey}
                        />
                    )}
                </PlotContainer>
            )}

            {!isComputing && (
                <div tw="absolute bottom-0 w-full text-xs text-right text-gray-700 p-0.5 pointer-events-none">
                    {visibleIndices.length} of {indices.length} rows
                </div>
            )}

            <MenuBar
                colorBy={colorByKey}
                sizeBy={sizeByKey}
                placeBy={placeByColumnKeys}
                filter={filter}
                embeddableColumns={embeddableColumnKeys}
                embeddableColumnsHints={embeddableColumnsHints}
                reductionMethod={reductionMethod ?? 'umap'}
                umapNNeighbors={umapNNeighbors}
                umapMetric={umapMetric ?? 'euclidean'}
                umapMinDist={umapMinDist}
                pcaNormalization={pcaNormalization ?? 'none'}
                onChangeColorBy={setStoredColorByKey}
                onChangeSizeBy={setSizeByKey}
                onChangePlaceBy={setStoredPlaceByColumnKeys}
                onChangeFilter={setFilter}
                onChangeReductionMethod={setReductionMethod}
                onChangeUmapNNeighbors={setUmapNNeighbors}
                onChangeUmapMetric={setUmapMetric}
                onChangeUmapMinDist={setUmapMinDist}
                onChangePCANormalization={setPCANormalization}
                onReset={resetPlot}
            />
        </MapContainer>
    );
};

SimilarityMap.defaultName = 'Similarity Map';
SimilarityMap.icon = SimilaritiesIcon;
SimilarityMap.key = 'similaritymap';
SimilarityMap.legacyKeys = ['simmap'];

export default SimilarityMap;

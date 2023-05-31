import * as d3 from 'd3';
import { TransferFunction } from '../../hooks/useColorTransferFunction';
import _ from 'lodash';
import { useEffect, useRef } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import { theme } from 'twin.macro';
import { BinKey, Bucket, HistogramData, Stack } from './types';

interface Props {
    width: number;
    height: number;
    histogram: HistogramData;
    hideUnfiltered: boolean;
    transferFunction: TransferFunction;
    onHoverBin: (kwargs?: { xKey?: BinKey; yKey?: BinKey }) => void;
}

const highlightRowsSelector = (d: Dataset) => d.setHighlightedRows;
const dehighlightAllSelector = (d: Dataset) => d.dehighlightAll;
const isIndexHighlightedSelector = (d: Dataset) => d.isIndexHighlighted;
const selectRowsSelector = (d: Dataset) => d.selectRows;

const Bars = ({
    width,
    height,
    histogram,
    transferFunction,
    hideUnfiltered,
    onHoverBin,
}: Props): JSX.Element => {
    const gRef = useRef<SVGGElement>(null);

    const setHighlightedRows = useDataset(highlightRowsSelector);
    const isIndexHighlighted = useDataset(isIndexHighlightedSelector);
    const dehighlightAll = useDataset(dehighlightAllSelector);
    const selectRows = useDataset(selectRowsSelector);

    useEffect(() => {
        const { all, filtered, xBins, yBins, binToRowIndices } = histogram;

        //update the plot
        if (!gRef) return;
        if (!all.length) return;

        const binIndexToAllMap = d3.rollup(
            all.flat(),
            (d) => d[0],
            (v) => v.xBin,
            (v) => v.yBin
        );

        const maxCount = hideUnfiltered
            ? _.max(
                  filtered[filtered.length - 1].map(([start, end]) =>
                      isNaN(end) ? start : end
                  )
              ) || 1
            : _.max(
                  all[all.length - 1].map(([start, end]) => (isNaN(end) ? start : end))
              ) || 1;

        const xAxisHeight = 14;
        const paddingTop = 14;
        const barHeight = height - xAxisHeight - paddingTop;

        const visibleXBins = hideUnfiltered
            ? xBins.filter(({ key }) =>
                  filtered[filtered.length - 1].map(({ xKey }) => xKey).includes(key)
              )
            : xBins;

        const barWidth = width / visibleXBins.length;

        const ticks = _.flatten(
            visibleXBins.map(({ min, max }, index) => [
                { range: min, domain: index * barWidth },
                { range: max, domain: (index + 1) * barWidth },
            ])
        );

        const xScale =
            histogram.kind === 'continuous'
                ? d3
                      .scaleLinear()
                      .domain([
                          _.minBy(visibleXBins, 'min')?.min || 0,
                          _.maxBy(visibleXBins, 'max')?.max || 0,
                      ])
                      .range([0, width])
                : d3
                      .scaleOrdinal<number, number>()
                      .domain(_.unionBy(ticks, 'range').map(({ range }) => range))
                      .range(_.unionBy(ticks, 'range').map(({ domain }) => domain));

        const yScale = d3.scaleLinear(
            [0, maxCount],
            [barHeight + paddingTop, paddingTop]
        );

        const group = d3.select(gRef.current);

        group
            .select('g.interactiveGroups')
            .selectAll<SVGSVGElement, SVGRectElement>('rect.interactiveArea')
            .data(xBins)
            .join(
                (enter) => enter.append('rect').attr('class', 'interactiveArea'),
                (update) => update,
                (exit) => exit.remove()
            )
            .attr('x', ({ min }) => xScale(min))
            .attr('width', ({ min, max }) => xScale(max) - xScale(min))
            .attr('y', 0)
            .attr('height', height)
            .style('opacity', 0)
            .style('cursor', 'pointer')
            .on('mouseenter', (_, bin) => {
                onHoverBin({ xKey: bin.key });
                const highlightMap = [] as boolean[];
                [...(binToRowIndices.get(bin.index)?.values() || [])]
                    .flat()
                    ?.forEach((index) => {
                        highlightMap[index] = true;
                    });
                setHighlightedRows(highlightMap);
            })
            .on('click', (_, bin) => {
                const indices = [
                    ...(binToRowIndices.get(bin.index)?.values() || []),
                ].flat();
                selectRows(indices);
            });

        group
            .select('g.allGroups')
            .selectAll<SVGSVGElement, SVGGElement>('g.all')
            .data(all)
            .join(
                (enter) => enter.append('g').attr('class', 'all'),
                (update) => update,
                (exit) => exit.remove()
            )
            .style('visibility', hideUnfiltered ? 'hidden' : 'visible')
            .selectAll('g.bucket-all')
            .data((d) => d.filter((d) => !isNaN(d[1])))
            .join(
                (enter) => {
                    const g = enter.append('g');
                    g.attr('class', 'bucket-all');
                    g.append('rect').attr('class', 'all');
                    return g;
                },
                (update) => update,
                (exit) => exit.remove()
            )
            .select('g.bucket-all > rect.all')
            .attr('y', (bucket) => {
                return (
                    yScale(bucket[0]) - Math.abs(yScale(bucket[0]) - yScale(bucket[1]))
                );
            })
            .attr('height', (bucket) => {
                return Math.max(0, Math.abs(yScale(bucket[0]) - yScale(bucket[1])));
            })
            .attr('x', ({ xBin }) => {
                const { min } = xBins[xBin];
                const scale = xScale(min) + 1;
                return scale;
            })
            .attr('width', ({ xBin }) => {
                const { min, max } = xBins[xBin];
                return Math.max(
                    0,
                    xScale(max) - xScale(min) - (max === xScale.domain()[1] ? 2 : 1)
                );
            })
            .style('fill', (bucket) =>
                transferFunction(yBins[bucket.yBin]?.value).alpha(0.2).css()
            );

        group
            .select('g.filteredGroups')
            .selectAll<SVGSVGElement, SVGGElement>('g.filtered')
            .data(filtered)
            .join(
                (enter) => {
                    const g = enter.append('g');
                    g.attr('class', 'filtered');
                    return g;
                },
                (update) => update,
                (exit) => {
                    exit.remove();
                }
            )
            .selectAll('g.bucket-filtered')
            .data((d) => d.filter((d) => !isNaN(d[1])))
            .join(
                (enter) => {
                    const g = enter.append('g');
                    g.attr('class', 'bucket-filtered');
                    g.append('rect').attr('class', 'filtered');
                    return g;
                },
                (update) => update,
                (exit) => exit.remove()
            )
            .select('g.bucket-filtered > rect.filtered')
            .attr('y', (bucket) => {
                const fullBucket = binIndexToAllMap.get(bucket.xBin)?.get(bucket.yBin);
                const bucketHeight = Math.abs(yScale(bucket[0]) - yScale(bucket[1]));
                if (hideUnfiltered || fullBucket === undefined) {
                    return yScale(bucket[0]) - bucketHeight - 1;
                }
                const fullBucketHeight = Math.abs(
                    yScale(fullBucket[0]) - yScale(fullBucket[1])
                );
                return (
                    yScale(bucket[0]) -
                    Math.abs(
                        yScale(bucket[0]) -
                            yScale(fullBucket[1]) -
                            (fullBucketHeight - bucketHeight)
                    )
                );
            })
            .attr('height', (bucket) => {
                return Math.max(0, Math.abs(yScale(bucket[0]) - yScale(bucket[1])));
            })
            .attr('x', ({ xBin }) => {
                const { min } = xBins[xBin];
                const scale = xScale(min) + 1;
                return scale;
            })
            .attr('width', ({ xBin }) => {
                const { min, max } = xBins[xBin];
                return Math.max(xScale(max) - xScale(min) - 1, 0);
            })
            .style('cursor', 'pointer')
            .on('mouseenter', (_, { xKey, yKey, xBin, yBin }) => {
                onHoverBin({ xKey, yKey });
                const highlightMap = [] as boolean[];
                binToRowIndices
                    .get(xBin)
                    ?.get(yBin)
                    ?.forEach((index) => (highlightMap[index] = true));
                setHighlightedRows(highlightMap);
            })
            .on('click', (_, { xBin, yBin }) => {
                const indices = binToRowIndices.get(xBin)?.get(yBin) || [];
                selectRows(indices);
            });

        group
            .select('g.filteredGroups')
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', width)
            .attr('height', Math.max(0, barHeight + paddingTop))
            .style('fill', theme`colors.white`)
            .on('mouseleave', (event) => {
                const node = event.currentTarget;
                onHoverBin();
                if (!node.parentNode?.parentNode?.contains(event.relatedTarget)) {
                    dehighlightAll();
                }
            });

        group.on('mouseleave', (event) => {
            const node = event.currentTarget;
            onHoverBin();
            if (!node.parentNode?.parentNode?.contains(event.relatedTarget)) {
                dehighlightAll();
            }
        });
    }, [
        histogram,
        setHighlightedRows,
        dehighlightAll,
        selectRows,
        width,
        height,
        hideUnfiltered,
        onHoverBin,
        transferFunction,
    ]);

    useEffect(() => {
        const binToRowIndices = histogram.binToRowIndices;
        const yBins = histogram.yBins;

        const areSomeHighlighted = isIndexHighlighted.some(
            (isHighlighted) => isHighlighted
        );

        const group = d3.select(gRef.current);
        group
            .selectAll<SVGGElement, Stack[]>('g.filtered')
            .selectAll<SVGRectElement, Bucket>('g.bucket-filtered > rect.filtered')
            .style('fill', (bucket) => {
                // possible performance gains if highlight changes are moved to own effect
                const indices =
                    binToRowIndices.get(bucket.xBin)?.get(bucket.yBin) || [];
                const highlighted = indices.some((index) => isIndexHighlighted[index]);
                return transferFunction(yBins[bucket.yBin]?.value)
                    .alpha(areSomeHighlighted && !highlighted ? 0.5 : 1)
                    .css();
            });
    }, [
        histogram.binToRowIndices,
        histogram.yBins,
        isIndexHighlighted,
        transferFunction,
    ]);

    return (
        <g ref={gRef}>
            <g className="interactiveGroups" />
            <g className="allGroups" />
            <g className="filteredGroups" />
            <rect className="background" />
        </g>
    );
};

export default Bars;

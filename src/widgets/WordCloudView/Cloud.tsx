import * as d3 from 'd3';
import d3Cloud from 'd3-cloud';
import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef } from 'react';
import 'twin.macro';
import { Dataset, useDataset } from '../../stores/dataset';
import seedrandom from 'seedrandom';

import { ColorsState, useColors } from '../../stores/colors';

const categoricalPaletteSelector = (c: ColorsState) => c.categoricalPalette;

export interface Word extends d3Cloud.Word {
    count: number;
    filteredCount: number;
    rowIds: number[];
    text: string;
}

interface Props {
    words: Record<string, Omit<Word, 'text'>>;
    scaling?: 'linear' | 'log' | 'sqrt';
    width: number;
    height: number;
    wordCount?: number;
    hideFiltered?: boolean;
}

const MIN_TEXT_SIZE = 10;
const MAX_TEXT_SIZE = 40;

const FONT_FAMILY = 'Impact';

const datasetSelector = (d: Dataset) => ({
    highlightRows: d.highlightRows,
    isIndexHighlighted: d.isIndexHighlighted,
    highlightedIndices: d.highlightedIndices,
    selectRows: d.selectRows,
    isIndexFiltered: d.isIndexFiltered,
    addFilter: d.addFilter,
});

export interface Ref {
    reset: () => void;
}

const Cloud = forwardRef<Ref, Props>(function Cloud(
    {
        words: incomingWords,
        scaling = 'linear',
        width,
        height,
        wordCount,
        hideFiltered = false,
    },
    ref
) {
    const svgRef = useRef<SVGSVGElement>(null);
    const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

    useImperativeHandle(ref, () => ({
        reset: () => {
            if (svgRef.current === null) return;
            if (zoomRef.current === null) return;

            d3.select(svgRef.current).call(zoomRef.current.transform, d3.zoomIdentity);
        },
    }));

    const words: Word[] = useMemo(
        () =>
            Object.entries(incomingWords)
                .map(([text, value]) => ({
                    text,
                    ...value,
                }))
                .sort((a, b) =>
                    hideFiltered ? b.filteredCount - a.filteredCount : b.count - a.count
                )
                .filter((word) => (hideFiltered ? word.filteredCount : word.count) > 0)
                .slice(0, wordCount),
        [hideFiltered, incomingWords, wordCount]
    );

    const {
        highlightRows,
        isIndexHighlighted,
        highlightedIndices,
        selectRows,
        isIndexFiltered,
    } = useDataset(datasetSelector);

    const isAnythingHighlighted = useMemo(
        () => highlightedIndices.length > 0,
        [highlightedIndices]
    );

    const categoricalPalette = useColors(categoricalPaletteSelector);

    const categoricalScale = useMemo(
        () => categoricalPalette.scale(),
        [categoricalPalette]
    );

    const [minSize, maxSize] = useMemo(() => {
        if (Object.keys(words).length === 0) return [0, 0];

        const counts = Object.values(words).map(({ count, filteredCount }) =>
            hideFiltered ? filteredCount : count || 0
        );
        return [Math.min(...counts), Math.max(...counts)];
    }, [hideFiltered, words]);

    const scale = useMemo(() => {
        switch (scaling) {
            case 'log':
                return d3
                    .scaleLog()
                    .domain([minSize, maxSize])
                    .range([MIN_TEXT_SIZE, MAX_TEXT_SIZE]);
            case 'sqrt':
                return d3
                    .scaleSqrt()
                    .domain([minSize, maxSize])
                    .range([MIN_TEXT_SIZE, MAX_TEXT_SIZE]);
            default:
                return d3
                    .scaleLinear()
                    .domain([minSize, maxSize])
                    .range([MIN_TEXT_SIZE, MAX_TEXT_SIZE]);
        }
    }, [maxSize, minSize, scaling]);

    useEffect(() => {
        const draw = (layedOutWords: Word[]) => {
            const svg = svgRef.current;

            if (svg === null) return;

            d3.select(svg)
                .attr('width', width)
                .attr('height', height)
                .select('g.words')
                .selectAll<d3.BaseType, Word>('text')
                .data(layedOutWords, (d) => d.text)
                .join(
                    (enter) =>
                        enter
                            .append('text')
                            .style('font-family', FONT_FAMILY)
                            .on('mouseover', (_, d) => {
                                highlightRows(d.rowIds);
                            })
                            .on('mouseout', () => highlightRows([]))
                            .on('click', (e, d) => {
                                selectRows(d.rowIds);
                                e.stopPropagation();
                            })
                            .attr('text-anchor', 'middle')
                            .text((d) => d.text || '')
                            .attr('fill', (d, i) =>
                                categoricalScale(
                                    i % categoricalPalette.maxClasses
                                ).hex()
                            ),
                    (update) => update,
                    (exit) => exit.remove()
                )
                .attr('font-size', (d) => `${d.size || 1}px`)
                .attr(
                    'transform',
                    (d) =>
                        `translate(${width / 2 + (d.x || 0)},${
                            height / 2 + (d.y || 0)
                        }) rotate(${d.rotate})`
                );
        };

        const layout = d3Cloud<Word>()
            .size([width, height])
            .words(words)
            .rotate((_, i) => ((i % 5) - 2) * 0)
            .padding(0.5)
            .font(FONT_FAMILY)
            .fontSize((d) => scale((hideFiltered ? d.filteredCount : d.count) || 1))
            .random(seedrandom('42'))
            .on('end', draw);
        layout.start();
    }, [
        words,
        scale,
        width,
        height,
        categoricalScale,
        categoricalPalette.maxClasses,
        highlightRows,
        selectRows,
        hideFiltered,
    ]);

    useEffect(() => {
        const svg = svgRef.current;

        if (svg === null) return;

        d3.select(svg)
            .attr('width', width)
            .attr('height', height)
            .select('g.words')
            .selectAll<d3.BaseType, Word>('text')
            .style('opacity', (d) =>
                !isAnythingHighlighted ||
                d.rowIds.some((index) => isIndexHighlighted[index])
                    ? 1
                    : 0.3
            )
            .attr('fill', (d, i) =>
                d.rowIds.some((index) => isIndexFiltered[index])
                    ? categoricalScale(i % categoricalPalette.maxClasses).hex()
                    : '#000000'
            )
            .on('mouseover', (_, d) => {
                d.rowIds.some((index) => isIndexFiltered[index]) &&
                    highlightRows(d.rowIds);
            })
            .on(
                'mouseout',
                (_, d) =>
                    d.rowIds.some((index) => isIndexFiltered[index]) &&
                    highlightRows([])
            );
    }, [
        categoricalPalette.maxClasses,
        categoricalScale,
        height,
        highlightRows,
        isAnythingHighlighted,
        isIndexFiltered,
        isIndexHighlighted,
        width,
    ]);

    useEffect(() => {
        const svg = svgRef.current;

        if (svg === null) return;

        const selection = d3.select(svg);

        zoomRef.current = d3
            .zoom<SVGSVGElement, unknown>()
            .on('zoom', (e) => {
                selection.select('g.words').attr('transform', e.transform);
            })
            .filter((event) => event.button === 1 || event.type === 'wheel');

        selection
            .on('click', () => {
                selectRows([]);
            })
            .call(zoomRef.current);
    }, [selectRows]);

    return (
        <svg ref={svgRef} tw="w-full h-full">
            <g className="words" />
        </svg>
    );
});

export default Cloud;

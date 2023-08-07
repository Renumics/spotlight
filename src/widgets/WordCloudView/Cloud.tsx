import * as d3 from 'd3';
import d3Cloud from 'd3-cloud';
import { useCallback, useEffect, useMemo, useRef } from 'react';
import 'twin.macro';
import { Dataset, useDataset } from '../../stores/dataset';
import seedrandom from 'seedrandom';

import { ColorsState, useColors } from '../../stores/colors';

const categoricalPaletteSelector = (c: ColorsState) => c.categoricalPalette;

export interface Word extends d3Cloud.Word {
    count: number;
    rowIds: number[];
    text: string;
}

interface Props {
    words: Record<string, Omit<Word, 'text'>>;
    scaling?: 'linear' | 'log' | 'sqrt';
    width: number;
    height: number;
    wordCount?: number;
}

const MIN_TEXT_SIZE = 10;
const MAX_TEXT_SIZE = 40;

const FONT_FAMILY = 'Impact';

const datasetSelector = (d: Dataset) => ({
    highlightRows: d.highlightRows,
    isIndexHighlighted: d.isIndexHighlighted,
    highlightedIndices: d.highlightedIndices,
    selectRows: d.selectRows,
});

const Cloud = ({
    words: incomingWords,
    scaling = 'linear',
    width,
    height,
    wordCount,
}: Props) => {
    const svgRef = useRef<SVGSVGElement>(null);

    const words: Word[] = useMemo(
        () =>
            Object.entries(incomingWords)
                .map(([text, value]) => ({
                    text,
                    // size: value.count,
                    ...value,
                }))
                .sort((a, b) => b.count - a.count)
                .slice(0, wordCount),
        [incomingWords, wordCount]
    );

    const { highlightRows, isIndexHighlighted, highlightedIndices, selectRows } =
        useDataset(datasetSelector);

    const isAnythingHighlighted = useMemo(
        () => highlightedIndices.length > 0,
        [highlightedIndices]
    );

    const categoricalPalette = useColors(categoricalPaletteSelector);

    const categoricalScale = useMemo(
        () => categoricalPalette.scale(),
        [categoricalPalette]
    );

    const [minCount, maxCount] = useMemo(() => {
        if (Object.keys(words).length === 0) return [0, 0];

        const counts = Object.values(words).map(({ count }) => count || 0);
        return [Math.min(...counts), Math.max(...counts)];
    }, [words]);

    const scale = useMemo(() => {
        switch (scaling) {
            case 'log':
                return d3
                    .scaleLog()
                    .domain([minCount, maxCount])
                    .range([MIN_TEXT_SIZE, MAX_TEXT_SIZE]);
            case 'sqrt':
                return d3
                    .scaleSqrt()
                    .domain([minCount, maxCount])
                    .range([MIN_TEXT_SIZE, MAX_TEXT_SIZE]);
            default:
                return d3
                    .scaleLinear()
                    .domain([minCount, maxCount])
                    .range([MIN_TEXT_SIZE, MAX_TEXT_SIZE]);
        }
    }, [maxCount, minCount, scaling]);

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
                    (enter) => enter.append('text').style('font-family', FONT_FAMILY),
                    (update) => update,
                    (exit) => exit.remove()
                )
                .attr('text-anchor', 'middle')
                .attr('font-size', (d) => `${d.size || 1}px`)
                .attr(
                    'transform',
                    (d) =>
                        `translate(${width / 2 + (d.x || 0)},${
                            height / 2 + (d.y || 0)
                        }) rotate(${d.rotate})`
                )
                .text((d) => d.text || '')
                .attr('fill', (d, i) =>
                    categoricalScale(i % categoricalPalette.maxClasses).hex()
                )
                .on('mouseover', (_, d) => {
                    highlightRows(d.rowIds);
                })
                .on('mouseout', () => highlightRows([]))
                .on('click', (e, d) => {
                    selectRows(d.rowIds);
                    e.stopPropagation();
                });
        };

        const layout = d3Cloud<Word>()
            .size([width, height])
            .words(words)
            .rotate((_, i) => ((i % 5) - 2) * 0)
            .padding(0.5)
            .font(FONT_FAMILY)
            .fontSize((d) => scale(d.count || 1))
            .random(seedrandom('42'))
            .on('end', draw);
        layout.start();
    }, [
        words,
        scale,
        width,
        height,
        minCount,
        categoricalScale,
        categoricalPalette.maxClasses,
        highlightRows,
        selectRows,
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
            );
    }, [height, highlightedIndices, isAnythingHighlighted, isIndexHighlighted, width]);

    useEffect(() => {
        const svg = svgRef.current;

        if (svg === null) return;

        const selection = d3.select(svg);

        const zoom = d3.zoom<SVGSVGElement, unknown>().on('zoom', (e) => {
            selection.select('g.words').attr('transform', e.transform);
        });

        selection
            .on('click', () => {
                selectRows([]);
            })
            .call(zoom);
    }, [selectRows]);

    return (
        <svg ref={svgRef} tw="w-full h-full">
            <g className="words" />
        </svg>
    );
};

export default Cloud;

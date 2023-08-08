import tw, { styled } from 'twin.macro';
import WordCloudIcon from '../../icons/WordCloud';
import { useDataset, Dataset } from '../../stores/dataset/dataset';
import { Widget } from '../types';
import { isStringColumn } from '../../types/dataset';
import useWidgetConfig from '../useWidgetConfig';
import MenuBar from './MenuBar';
import { ComponentProps, useCallback, useMemo, useRef } from 'react';
import _ from 'lodash';
import Cloud, { Ref as CloudRef } from './Cloud';
import useSize from '../../hooks/useSize';

const WordViewContainer = styled.div`
    ${tw`bg-gray-100 border-gray-400 w-full h-full overflow-hidden relative`}
`;

const CloudContainer = tw.div`flex top-0 left-0 w-full h-full`;

const datasetSelector = (d: Dataset) => ({
    columns: d.columns,
    columnData: d.columnData,
    isIndexFiltered: d.isIndexFiltered,
});

const WordCloudView: Widget = () => {
    const { columns, columnData, isIndexFiltered } = useDataset(datasetSelector);

    const cloudContainerRef = useRef<HTMLDivElement>(null);
    const cloudRef = useRef<CloudRef>(null);

    const ploaceableColumnsKeys = useMemo(
        () => columns.filter((c) => isStringColumn(c)).map(({ key }) => key),
        [columns]
    );

    const [_axisColumnKey, setAxisColumnKey] = useWidgetConfig<string>(
        'wordCloudAxisColumnKey',
        columns.filter((c) => isStringColumn(c)).map(({ key }) => key)[0] ?? ''
    );

    const axisColumnKey =
        _axisColumnKey && ploaceableColumnsKeys.includes(_axisColumnKey)
            ? _axisColumnKey
            : columns.filter((c) => isStringColumn(c)).map(({ key }) => key)[0] ?? '';

    const [splitStringsBy, setSplitStringsBy] = useWidgetConfig<string>(
        'splitStringsBy',
        '[\\s,\\.;:!?\\-\\–\\—\\(\\)\\[\\]\\{\\}]'
    );

    const [scaling, setScaling] = useWidgetConfig<
        ComponentProps<typeof Cloud>['scaling']
    >('scaling', 'log');

    const [wordsToShowCount, setWordCount] = useWidgetConfig<number>('wordCount');

    const columnToPlaceBy = useMemo(
        () => columns.find((c) => c.key === axisColumnKey),
        [columns, axisColumnKey]
    );

    const [wordCounts, uniqueWordsCount] = useMemo(() => {
        if (columnToPlaceBy === undefined) return [{}, 0];

        const rows = columnData[axisColumnKey] as string[];

        if (!rows) {
            return [{}, 0];
        }

        const splitter =
            splitStringsBy.length > 1 ? new RegExp(splitStringsBy) : splitStringsBy;

        let uniqueWordsCount = 0;
        const wordCounts = rows.reduce((acc, line, index) => {
            line.split(splitter).forEach((word) => {
                if (word.length < 1) return acc;
                if (word in acc) {
                    acc[word].count++;
                    acc[word].rowIds.push(index);
                } else {
                    acc[word] = { count: 1, rowIds: [index] };
                    uniqueWordsCount++;
                }
            });
            return acc;
        }, {} as Record<string, { count: number; rowIds: number[] }>);
        return [wordCounts, uniqueWordsCount];
    }, [axisColumnKey, columnData, columnToPlaceBy, splitStringsBy]);

    const wordCountsWithFiltered = useMemo(
        () =>
            Object.entries(wordCounts).reduce((acc, [key, word]) => {
                acc[key] = {
                    ...word,
                    filteredCount: word.rowIds.filter((rowId) => isIndexFiltered[rowId])
                        .length,
                };
                return acc;
            }, {} as Record<string, { count: number; rowIds: number[]; filteredCount: number }>),
        [wordCounts, isIndexFiltered]
    );

    const [hideFiltered, setHideFiltered] = useWidgetConfig<boolean>(
        'hideFiltered',
        false
    );

    const resetZoom = useCallback(() => {
        if (cloudRef.current) {
            cloudRef.current.reset();
        }
    }, []);

    const cloudContainerSize = useSize(cloudContainerRef);

    return (
        <WordViewContainer tw="bg-white">
            <CloudContainer ref={cloudContainerRef}>
                <Cloud
                    ref={cloudRef}
                    words={wordCountsWithFiltered}
                    scaling={scaling}
                    width={cloudContainerSize.width}
                    height={cloudContainerSize.height}
                    wordCount={wordsToShowCount}
                    hideFiltered={hideFiltered}
                />
            </CloudContainer>
            <MenuBar
                wordCloudBy={axisColumnKey}
                placeableColumns={ploaceableColumnsKeys}
                scaling={scaling}
                onChangeScaling={setScaling}
                filter={hideFiltered || false}
                onChangeWordCloudolumn={setAxisColumnKey}
                onChangeFilter={setHideFiltered}
                onReset={resetZoom}
                minWordCount={1}
                maxWordCount={uniqueWordsCount}
                wordCount={wordsToShowCount ?? uniqueWordsCount}
                onChangeWordCount={setWordCount}
            />
        </WordViewContainer>
    );
};

WordCloudView.defaultName = 'Word Cloud';
WordCloudView.icon = WordCloudIcon;
WordCloudView.key = 'wordcloud';

export default WordCloudView;

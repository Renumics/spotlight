import tw, { styled } from 'twin.macro';
import WordCloudIcon from '../../icons/WordCloud';
import { useDataset, Dataset } from '../../stores/dataset/dataset';
import { Widget } from '../types';
import { DataColumn, isCategoricalColumn, isStringColumn } from '../../types/dataset';
import useWidgetConfig from '../useWidgetConfig';
import MenuBar from './MenuBar';
import { ComponentProps, useCallback, useMemo, useRef } from 'react';
import Cloud, { Ref as CloudRef } from './Cloud';
import useSize from '../../hooks/useSize';
import defaultStopwords from './stopwords.json';
import Info from '../../components/ui/Info';

const WordViewContainer = styled.div`
    ${tw`bg-gray-100 border-gray-400 w-full h-full overflow-hidden relative`}
`;

const CloudContainer = tw.div`flex top-0 left-0 w-full h-full`;

const datasetSelector = (d: Dataset) => ({
    columns: d.columns,
    columnData: d.columnData,
    isIndexFiltered: d.isIndexFiltered,
});

const isAllowedColumn = (c: DataColumn) => isStringColumn(c) || isCategoricalColumn(c);

const WordCloudView: Widget = () => {
    const { columns, columnData, isIndexFiltered } = useDataset(datasetSelector);

    const cloudContainerRef = useRef<HTMLDivElement>(null);
    const cloudRef = useRef<CloudRef>(null);

    const ploaceableColumnsKeys = useMemo(
        () => columns.filter((c) => isAllowedColumn(c)).map(({ key }) => key),
        [columns]
    );

    const [_cloudByColumnKey, setCloudByColumnKey] =
        useWidgetConfig<string>('cloudByColumnKey');

    const cloudByColumnKey =
        _cloudByColumnKey && ploaceableColumnsKeys.includes(_cloudByColumnKey)
            ? _cloudByColumnKey
            : columns.filter((c) => isAllowedColumn(c)).map(({ key }) => key)[0] ?? '';

    const [minWordLength, setMinWordLength] = useWidgetConfig<number>(
        'minWordLength',
        3
    );

    const splitStringsBy = '[\\s,\\.;:!?\\-\\–\\—\\(\\)\\[\\]\\{\\}"\']';

    const [stopwords, setStopwords] = useWidgetConfig<string[]>(
        'stopwords',
        defaultStopwords
    );

    const [scaling, setScaling] = useWidgetConfig<
        ComponentProps<typeof Cloud>['scaling']
    >('scaling', 'log');

    const [wordsToShowCount, setWordCount] = useWidgetConfig<number>('wordCount', 100);

    const columnToPlaceBy = useMemo(
        () => columns.find((c) => c.key === cloudByColumnKey),
        [columns, cloudByColumnKey]
    );

    const [wordCounts, uniqueWordsCount] = useMemo(() => {
        if (columnToPlaceBy === undefined) return [{}, 0];

        const data = columnData[columnToPlaceBy.key];
        const rows: string[] = isCategoricalColumn(columnToPlaceBy)
            ? Array.from(data).map(
                  (v) => `${columnToPlaceBy.type.invertedCategories[v]}`
              )
            : (columnData[columnToPlaceBy.key] as string[]);

        if (!rows) {
            return [{}, 0];
        }

        const splitter =
            splitStringsBy.length > 1 ? new RegExp(splitStringsBy) : splitStringsBy;

        const splitRows = rows.map((row) => (row ?? '').toLowerCase().split(splitter));

        let uniqueWordsCount = 0;
        const wordCounts = splitRows.reduce((acc, line, index) => {
            line.forEach((word) => {
                const lower = word.toLowerCase();
                if (!stopwords.includes(lower) && lower.length >= minWordLength) {
                    if (lower.length < 1) return acc;
                    if (lower in acc) {
                        acc[lower].count++;
                        acc[lower].rowIds.push(index);
                    } else {
                        acc[lower] = { count: 1, rowIds: [index] };
                        uniqueWordsCount++;
                    }
                }
            });
            return acc;
        }, {} as Record<string, { count: number; rowIds: number[] }>);
        return [wordCounts, uniqueWordsCount];
    }, [stopwords, columnData, columnToPlaceBy, minWordLength, splitStringsBy]);

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
                {Object.keys(wordCountsWithFiltered).length > 0 ? (
                    <Cloud
                        ref={cloudRef}
                        words={wordCountsWithFiltered}
                        scaling={scaling}
                        width={cloudContainerSize.width}
                        height={cloudContainerSize.height}
                        wordCount={wordsToShowCount}
                        hideFiltered={hideFiltered}
                    />
                ) : (
                    <Info>
                        No Words to Cloud by
                        <br />
                        Select a Column to Cloud by or alter Stopwords.
                    </Info>
                )}
            </CloudContainer>
            <MenuBar
                wordCloudBy={cloudByColumnKey}
                placeableColumns={ploaceableColumnsKeys}
                scaling={scaling}
                onChangeScaling={setScaling}
                filter={hideFiltered || false}
                onChangeWordCloudColumn={setCloudByColumnKey}
                onChangeFilter={setHideFiltered}
                onReset={resetZoom}
                minWordCount={1}
                maxWordCount={uniqueWordsCount}
                wordCount={wordsToShowCount ?? uniqueWordsCount}
                onChangeWordCount={setWordCount}
                stopwords={stopwords}
                onChangeStopwords={setStopwords}
                minWordLength={minWordLength}
                maxWordLength={15}
                onChangeMinWordLength={setMinWordLength}
            />
        </WordViewContainer>
    );
};

WordCloudView.defaultName = 'Word Cloud';
WordCloudView.icon = WordCloudIcon;
WordCloudView.key = 'wordcloud';

export default WordCloudView;

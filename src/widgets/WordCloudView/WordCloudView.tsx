import tw, { styled } from 'twin.macro';
import WordCloudIcon from '../../icons/WordCloud';
import { useDataset, Dataset } from '../../stores/dataset/dataset';
import { Widget } from '../types';
import { isStringColumn } from '../../types/dataset';
import useWidgetConfig from '../useWidgetConfig';
import MenuBar from './MenuBar';
import { ComponentProps, useMemo, useRef } from 'react';
import _ from 'lodash';
import Cloud from './Cloud';
import useSize from '../../hooks/useSize';

const WordViewContainer = styled.div`
    ${tw`bg-gray-100 border-gray-400 w-full h-full overflow-hidden relative`}
`;

const CloudContainer = tw.div`flex top-0 left-0 w-full h-full`;

const datasetSelector = (d: Dataset) => ({
    columns: d.columns,
    columnData: d.columnData,
});

const WordCloudView: Widget = () => {
    const { columns, columnData } = useDataset(datasetSelector);

    const cloudContainerRef = useRef<HTMLDivElement>(null);

    const placeableColumns = useMemo(
        () => columns.filter((c) => isStringColumn(c)).map(({ key }) => key),
        [columns]
    );

    const [axisColumnKey, setAxisColumnKey] = useWidgetConfig<string>(
        'wordCloudAxisColumnKey',
        ''
    );

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

    const [filter, setFilter] = useWidgetConfig<boolean>('filter', false);

    const cloudContainerSize = useSize(cloudContainerRef);

    return (
        <WordViewContainer tw="bg-white">
            <CloudContainer ref={cloudContainerRef}>
                <Cloud
                    words={wordCounts}
                    scaling={scaling}
                    width={cloudContainerSize.width}
                    height={cloudContainerSize.height}
                    wordCount={wordsToShowCount}
                />
            </CloudContainer>
            <MenuBar
                wordCloudBy={axisColumnKey}
                placeableColumns={placeableColumns}
                scaling={scaling}
                onChangeScaling={setScaling}
                filter={filter || false}
                onChangeWordCloudolumn={setAxisColumnKey}
                onChangeFilter={setFilter}
                onReset={() => null}
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

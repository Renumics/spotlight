import { isAudio } from '../datatypes';
import { useEffect, useMemo, useState } from 'react';
import { Lens } from '../types';
import AudioViewer from '../components/shared/AudioViewer';
import { useDataset } from '../stores/dataset';
import api from '../api';
import useSetting from './useSetting';

async function fetchWaveform(row: number, column: string): Promise<number[]> {
    const generationId = useDataset.getState().generationID;
    const waveform = await api.table.getWaveform({ row, column, generationId });
    return waveform;
}

const AudioLens: Lens = ({ rowIndex, columns, urls, values }) => {
    const windowIndex = columns.findIndex((col) => col.type.kind === 'Window');
    const audioIndex = columns.findIndex((col) => col.type.kind === 'Audio');
    const window = values[windowIndex] as [number, number] | undefined;
    const url = urls[audioIndex];
    const optional = columns[windowIndex]?.optional ?? false;

    const [waveform, setWaveform] = useState<number[]>();

    const [repeat, setRepeat] = useSetting('repeat', false);

    const [autoplay, setAutoplay] = useSetting('autoplay', false);

    useEffect(() => {
        fetchWaveform(rowIndex, columns[audioIndex].key).then((waveform) => {
            setWaveform(waveform);
        });
    }, [rowIndex, columns, audioIndex]);

    const windows = useMemo(() => (window ? [window] : []), [window]);

    return (
        <AudioViewer
            windows={windows}
            url={url}
            peaks={waveform}
            editable={false}
            optional={optional}
            showControls={true}
            repeat={repeat}
            onChangeRepeat={setRepeat}
            autoplay={autoplay}
            onChangeAutoplay={setAutoplay}
        />
    );
};

AudioLens.key = 'AudioView';
AudioLens.defaultHeight = 120;
AudioLens.displayName = 'Audio Player';
AudioLens.dataTypes = ['Audio', 'Window'];
AudioLens.multi = true;
AudioLens.filterAllowedColumns = (allColumns, selectedColumns) => {
    if (selectedColumns.length === 2) return [];
    switch (selectedColumns[0]?.type.kind) {
        case 'Audio':
            return allColumns.filter((col) => col.type.kind === 'Window');
        case 'Window':
            return allColumns.filter((col) => col.type.kind === 'Audio');
    }
    return allColumns.filter((col) => ['Audio', 'Window'].includes(col.type.kind));
};
AudioLens.isSatisfied = (columns) => {
    return columns.some((col) => isAudio(col.type));
};

export default AudioLens;

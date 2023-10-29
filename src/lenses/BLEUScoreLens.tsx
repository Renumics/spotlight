import { Lens, DataColumn } from '../types';
import { bleu } from 'bleu-score';

const BLEUScoreLens: Lens = ({ values }) => {
    const N = 4;
    const bleuScores: number[] = Array(N).fill(0);
    for (let n = 1; n <= N; n++) {
        bleuScores[n - 1] = bleu(values[0], values[1], n);
    }

    return (
        <div tw="p-1 text-xs" style={{ height: '100%', overflowY: 'scroll' }}>
            {bleuScores.map((score, index) => (
                <div key={index}>{`BLEU score using ${index + 1}-gram: ${score}`}</div>
            ))}
        </div>
    );
};

BLEUScoreLens.key = 'BLEUScoreView';
BLEUScoreLens.dataTypes = ['str'];
BLEUScoreLens.defaultHeight = 22;
BLEUScoreLens.minHeight = 22;
BLEUScoreLens.maxHeight = 64;
BLEUScoreLens.displayName = 'BLEU Score';
BLEUScoreLens.multi = true;
BLEUScoreLens.filterAllowedColumns = (allColumns, selectedColumns) => {
    if (selectedColumns.length === 2) return [];
    const selectedKeys = selectedColumns.map((selectedCol) => selectedCol.key);
    return allColumns.filter(({ type, key }) => {
        return type.kind === 'str' && !selectedKeys.includes(key);
    });
};
BLEUScoreLens.isSatisfied = (columns: DataColumn[]) => {
    return columns.length === 2;
};

export default BLEUScoreLens;

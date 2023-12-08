import { Lens, DataColumn } from '../types';
import { bleu } from 'bleu-score';
import 'twin.macro';

const BLEUScoreLens: Lens = ({ values }) => {
    const N = 4;

    const reference: string = values[0] as string;
    const candidate: string = values[1] as string;

    const bleuScores: number[] = Array(N).fill(0);
    for (let n = 1; n <= N; n++) {
        bleuScores[n - 1] = bleu(reference, candidate, n);
    }

    return (
        <div tw="p-1 text-sm">
            {bleuScores.map((score, index) => (
                <div key={index}>{`BLEU (${index + 1}-gram): ${score}`}</div>
            ))}
        </div>
    );
};

BLEUScoreLens.key = 'BLEUScoreView';
BLEUScoreLens.dataTypes = ['str'];
BLEUScoreLens.defaultHeight = 90;
BLEUScoreLens.minHeight = 90;
BLEUScoreLens.maxHeight = 90;
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

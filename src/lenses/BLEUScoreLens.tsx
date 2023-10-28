import { Lens, DataColumn } from '../types';

function CalcBLEU(reference: string, candidate: string, maxN: number) {
    // Tokenize the reference and candidate sentences
    const referenceTokens = reference.split(' ');
    const candidateTokens = candidate.split(' ');

    // Calculate n-gram precision
    const precision: number[] = Array(maxN).fill(0);

    for (let n = 1; n <= maxN; n++) {
        const referenceNgrams: { [key: string]: number } = {};
        const candidateNgrams: { [key: string]: number } = {};

        for (let i = 0; i < referenceTokens.length - n + 1; i++) {
            const ngram = referenceTokens.slice(i, i + n).join(' ');
            referenceNgrams[ngram] = (referenceNgrams[ngram] || 0) + 1;
        }

        for (let i = 0; i < candidateTokens.length - n + 1; i++) {
            const ngram = candidateTokens.slice(i, i + n).join(' ');
            candidateNgrams[ngram] = (candidateNgrams[ngram] || 0) + 1; // if
        }

        let totalNgramMatches = 0;
        for (const ngram in candidateNgrams) {
            if (ngram in referenceNgrams) {
                // Clipped precision
                totalNgramMatches += Math.min(
                    candidateNgrams[ngram],
                    referenceNgrams[ngram]
                );
            }
        }

        let totalPredictedNgrams = candidateTokens.length - n + 1;
        precision[n - 1] = totalNgramMatches / totalPredictedNgrams;
    }

    // Calculate brevity penalty
    const referenceLength = referenceTokens.length;
    const candidateLength = candidateTokens.length;
    const brevityPenalty =
        candidateLength > referenceLength
            ? 1
            : Math.exp(1 - referenceLength / candidateLength);

    // Calculate BLEU score
    const geometricMean = Math.pow(
        precision.reduce((acc, p) => acc * p, 1),
        1 / maxN
    );
    const bleuScore = brevityPenalty * geometricMean;

    return bleuScore;
}

const BLEUScoreLens: Lens = ({ values }) => {
    const N = 4;
    const bleu: number[] = Array(N).fill(0);
    for (let n = 1; n <= N; n++) {
        bleu[n - 1] = CalcBLEU(values[0], values[1], n);
    }

    return (
        <div tw="p-1 text-xs" style="height: 100%; overflow-y: scroll;">
            {bleu.map((score, index) => (
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

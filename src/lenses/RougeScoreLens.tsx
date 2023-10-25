import { Lens } from '../types';
import 'twin.macro';
import rouge from 'rouge';
import { formatNumber } from '../dataformat';

const calculateRougeScore = (values: unknown[]) => {
    return rouge.n(values[0], values[1]);
};

const RougeScoreLens: Lens = ({ values }) => {
    const result = calculateRougeScore(values);
    return (
        <div tw="text-sm truncate px-1 py-0.5 flex items-center h-full">
            Rouge score: {formatNumber(result)}
        </div>
    );
};

RougeScoreLens.key = 'RougeScoreView';
RougeScoreLens.dataTypes = ['str'];
RougeScoreLens.defaultHeight = 22;
RougeScoreLens.minHeight = 22;
RougeScoreLens.maxHeight = 64;
RougeScoreLens.multi = true;
RougeScoreLens.displayName = 'ROUGE Score';
RougeScoreLens.filterAllowedColumns = (allColumns, selectedColumns) => {
    if (selectedColumns.length === 2) return [];
    else
        return allColumns.filter(({ type, key }) => {
            const isNotSelected = (key: string) => {
                return selectedColumns.filter((selectedCol) => {
                    selectedCol.key !== key;
                });
            };
            return type.kind === 'str' && isNotSelected(key);
        });
};
RougeScoreLens.isSatisfied = (columns) => {
    if (columns.length === 2) return true;
    return false;
};
export default RougeScoreLens;

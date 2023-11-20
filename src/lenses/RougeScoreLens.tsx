import { Lens } from '../types';
import 'twin.macro';
import rouge from 'rouge';
import { useDataformat } from '../dataformat';

const RougeScoreLens: Lens<string> = ({ values }) => {
    const rouge1 = rouge.n(values[0], values[1], 1);
    const rouge2 = rouge.n(values[0], values[1], 2);

    const formatter = useDataformat();

    return (
        <div>
            <div tw="text-sm truncate px-1 py-0.5 flex items-center h-full">
                Rouge 1: {formatter.formatFloat(rouge1)}
            </div>
            <div tw="text-sm truncate px-1 py-0.5 flex items-center h-full">
                Rouge 2: {formatter.formatFloat(rouge2)}
            </div>
        </div>
    );
};

RougeScoreLens.key = 'RougeScoreView';
RougeScoreLens.dataTypes = ['str'];
RougeScoreLens.defaultHeight = 50;
RougeScoreLens.minHeight = 50;
RougeScoreLens.maxHeight = 100;
RougeScoreLens.multi = true;
RougeScoreLens.displayName = 'ROUGE Score';

RougeScoreLens.filterAllowedColumns = (allColumns, selectedColumns) => {
    if (selectedColumns.length === 2) return [];
    const selectedKeys = selectedColumns.map((selectedCol) => selectedCol.key);
    return allColumns.filter(({ type, key }) => {
        return type.kind === 'str' && !selectedKeys.includes(key);
    });
};
RougeScoreLens.isSatisfied = (columns) => columns.length === 2;

export default RougeScoreLens;

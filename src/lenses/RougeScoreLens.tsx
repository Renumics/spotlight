import { Lens } from '../types';
import 'twin.macro';
import rouge from 'rouge';
import { useDataformat } from '../dataformat';

const RougeScoreLens: Lens<string> = ({ values }) => {
    const a = values[0] ?? '';
    const b = values[1] ?? '';

    const anyEmpty = a.length === 0 || b.length === 0;

    const rouge1 = anyEmpty ? 0 : rouge.n(a, b, 1);
    const rouge2 = anyEmpty ? 0 : rouge.n(a, b, 2);

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

RougeScoreLens.key = 'RougeScore';
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

import { Lens, DataColumn } from '../types';

function CalcBLEU(col1: string, col2: string) {
    // TODO
    return `${col1.length + col2.length}`;
}

const BLEULens: Lens = ({ values }) => {
    var bleu = CalcBLEU(values[0], values[1]);
    return (
        <div tw="w-full h-full overflow-y-auto p-1 text-xs whitespace-pre-wrap">
            {bleu}
        </div>
    );
};

BLEULens.key = 'BLEUView';
BLEULens.dataTypes = ['str'];
BLEULens.defaultHeight = 22;
BLEULens.minHeight = 22;
BLEULens.maxHeight = 64;
BLEULens.displayName = 'BLEULens';
BLEULens.multi = true;
BLEULens.isSatisfied = (columns: DataColumn[]) => {
    return columns.length == 2;
};

export default BLEULens;

import 'twin.macro';
import { Lens } from '../types';
import JsonView from '@uiw/react-json-view';
import { isCategorical, isSequence } from '../datatypes';
import { useMemo } from 'react';

const THEME = { backgroundColor: 'transparent' };

const ArrayLens: Lens = ({ value, column }) => {
    const array = useMemo(() => {
        const columnType = column.type;
        if (!isSequence(columnType)) return value;

        const innerType = columnType.dtype;
        if (!isCategorical(innerType)) return value;

        return (value as number[]).map((x) => innerType.invertedCategories[x]);
    }, [value, column]);

    return (
        <div tw="w-full h-full overflow-y-auto">
            <JsonView
                value={array as object}
                style={THEME}
                displayObjectSize={false}
                displayDataTypes={false}
                highlightUpdates={false}
                enableClipboard={false}
            />
        </div>
    );
};

ArrayLens.key = 'ArrayLens';
ArrayLens.dataTypes = ['array', 'Embedding', 'Window', 'BoundingBox', 'Sequence'];
ArrayLens.defaultHeight = 128;
ArrayLens.minHeight = 22;
ArrayLens.maxHeight = 512;
ArrayLens.displayName = 'Array';

export default ArrayLens;

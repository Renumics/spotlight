import 'twin.macro';
import ScalarValue from '../components/ScalarValue';
import { Lens } from '../types';
import { useSettings } from '../systems/lenses';

const ScalarLens: Lens<number> = ({ value, column }) => {
    useSettings({
        foo: { value: 5 },
    });

    return (
        <div tw="text-sm truncate px-1 py-0.5 flex items-center h-full">
            <ScalarValue value={value} column={column} />
        </div>
    );
};

ScalarLens.kind = 'ScalarView';
ScalarLens.dataTypes = ['int', 'float', 'bool', 'str', 'datetime', 'Category'];
ScalarLens.defaultHeight = 22;
ScalarLens.minHeight = 22;
ScalarLens.maxHeight = 64;
ScalarLens.displayName = 'Value';

export default ScalarLens;

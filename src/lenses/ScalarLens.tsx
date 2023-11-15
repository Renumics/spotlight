import 'twin.macro';
import ScalarValue from '../components/ScalarValue';
import { Lens } from '../types';

const settings = {
    foo: { value: 16 },
    bar: { value: 'foobar' },
} as const;

const ScalarLens: Lens<number, typeof settings> = ({ value, column, settings }) => {
    return (
        <div tw="text-sm truncate px-1 py-0.5 flex items-center h-full">
            <ScalarValue value={value} column={column} />
            {settings.foo.value} {settings.bar.value}
        </div>
    );
};
ScalarLens.kind = 'ScalarView';
ScalarLens.dataTypes = ['int', 'float', 'bool', 'str', 'datetime', 'Category'];
ScalarLens.settings = settings;
ScalarLens.defaultHeight = 22;
ScalarLens.minHeight = 22;
ScalarLens.maxHeight = 64;
ScalarLens.displayName = 'Value';

export default ScalarLens;

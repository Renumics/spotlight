import 'twin.macro';
import ScalarValue from '../components/ScalarValue';
import { Lens } from '../types';

const defaultSettings = { foo: 10 };

/*
 * TODO: build new hook for lens settings
 *  takes in name, default value, and an optional menu item
 *
const menus = {}
function useSetting(name: str, value: unknown) {
    //const lensId = useLensId()
    const lensId = 5

    // return existing menu or build from scratch
}
*/

const ScalarLens: Lens<number> = ({ value, column }) => {
    // TODO: implement lens settings like this?
    //       const foo = useSetting('foo', 5)

    return (
        <div tw="text-sm truncate px-1 py-0.5 flex items-center h-full">
            <ScalarValue value={value + foo} column={column} />
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

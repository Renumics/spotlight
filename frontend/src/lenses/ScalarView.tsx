import 'twin.macro';
import ScalarValue from '../components/ScalarValue';
import { View } from './types';

const ScalarView: View = ({ value, column }) => {
    return (
        <div tw="text-sm truncate px-1 py-0.5 flex items-center h-full">
            <ScalarValue value={value} column={column} />
        </div>
    );
};

ScalarView.dataTypes = ['int', 'float', 'bool', 'str', 'datetime', 'Category'];

ScalarView.defaultHeight = 22;
ScalarView.minHeight = 22;
ScalarView.maxHeight = 64;
ScalarView.displayName = 'Value';

export default ScalarView;

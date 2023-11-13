import 'twin.macro';
import ScalarValue from '../components/ScalarValue';
import { Lens } from '../types';
import { useId, useState } from 'react';

const LensGroup = () => {
    // TODO: setup context for settings etc
    const id = useId();
    const settings = useState({});

    return <></>;
};

interface SettingSpec<T = unknown> {
    key: string;
    name: string;
    type: string;
}

// TODO: store in LensContext
const lensSettings: Record<string, Record<string, SettingSpec>> = {};

function useSetting<T>(key: string, value: T) {
    const lensId = 5;

    if (!lensSettings[lensId]) {
        lensSettings[lensId] = {};
    }

    lensSettings[lensId][key] = {
        key: key,
        name: key,
        type: value?.constructor.name ?? 'unknown',
    };
}

// render menu for the lens group
const LensMenu = () => {
    //TODO: implement
    // const { settings } = useLensGroupContext()
};

const ScalarLens: Lens<number> = ({ value, column }) => {
    // TODO: implement lens settings like this?
    //       const foo = useSetting('foo', 5)

    // const {foo, bar} = useSettings({
    //   foo: {value: 5, render: () => {}, key: 'notfoo'},
    //   bar: 'foobar'
    // })

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

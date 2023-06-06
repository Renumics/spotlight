import 'twin.macro';
import dataformat from '../dataformat';
import { Lens } from '../types';

const ArrayLens: Lens = ({ value }) => {
    const array = value as Array<number>;

    return (
        <div tw="text-xs px-1 py-0.5 flex flex-wrap content-center items-center h-full">
            <div tw="font-bold">[</div>
            {array.map((value, i) => (
                <div tw="m-1" key={i}>
                    {dataformat.formatNumber(value)}
                </div>
            ))}
            <div tw="font-bold">]</div>
        </div>
    );
};

ArrayLens.key = 'ArrayLens';
ArrayLens.dataTypes = ['array', 'Embedding'];
ArrayLens.defaultHeight = 22;
ArrayLens.minHeight = 22;
ArrayLens.maxHeight = 128;
ArrayLens.displayName = 'Array';

export default ArrayLens;

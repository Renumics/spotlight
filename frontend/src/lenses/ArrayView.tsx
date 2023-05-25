import 'twin.macro';
import { View } from './types';
import dataformat from '../dataformat';

const ArrayView: View = ({ value }) => {
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

ArrayView.dataTypes = ['array', 'Embedding'];
ArrayView.defaultHeight = 22;
ArrayView.minHeight = 22;
ArrayView.maxHeight = 128;
ArrayView.displayName = 'Array';

export default ArrayView;

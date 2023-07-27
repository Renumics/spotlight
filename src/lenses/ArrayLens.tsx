import 'twin.macro';
import dataformat from '../dataformat';
import { Lens } from '../types';

interface ArrayProps {
    value: Array<number>;
}

const ArrayComponent = ({ value }: ArrayProps): JSX.Element => {
    return (
        <>
            <div tw="font-bold">[</div>
            {value.map((element, i) =>
                Array.isArray(element) ? (
                    <ArrayComponent value={element} key={i} />
                ) : (
                    <div tw="m-1" key={i}>
                        {dataformat.formatNumber(element)}
                    </div>
                )
            )}
            <div tw="font-bold">]</div>
        </>
    );
};

const ArrayLens: Lens = ({ value }) => {
    const array = value as Array<number>;

    return (
        <div tw="text-xs px-1 py-0.5 flex flex-wrap content-center items-center h-full">
            <ArrayComponent value={array} />
        </div>
    );
};

ArrayLens.key = 'ArrayLens';
ArrayLens.dataTypes = ['array', 'Embedding', 'Window'];
ArrayLens.defaultHeight = 22;
ArrayLens.minHeight = 22;
ArrayLens.maxHeight = 128;
ArrayLens.displayName = 'Array';

export default ArrayLens;

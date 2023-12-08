import { DataType } from '../../datatypes';

const columnWidthByType: Record<DataType['kind'], number> = {
    int: 92,
    float: 110,
    bool: 92,
    str: 256,
    array: 128,
    datetime: 192,
    Embedding: 128,
    Audio: 200,
    Video: 200,
    Window: 150,
    BoundingBox: 128,
    Mesh: 200,
    Image: 200,
    Sequence1D: 200,
    Category: 128,
    Sequence: 128,
    Unknown: 128,
};

export default columnWidthByType;

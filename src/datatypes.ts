// kind definitions
export const datakinds = [
    'int',
    'float',
    'bool',
    'str',
    'array',
    'datetime',
    'Mesh',
    'Sequence1D',
    'Embedding',
    'Image',
    'Audio',
    'Video',
    'Category',
    'Window',
    'BoundingBox',
    'Sequence',
    'Unknown',
] as const;
export type DataKind = typeof datakinds[number];

export interface BaseDataType<
    K extends DataKind,
    L extends boolean = false,
    B extends boolean = false
> {
    kind: K;
    binary: B;
    lazy: L;
    optional: boolean;
}

// type definitions
export type UnknownDataType = BaseDataType<'Unknown'>;
export type IntegerDataType = BaseDataType<'int'>;
export type FloatDataType = BaseDataType<'float'>;
export type BooleanDataType = BaseDataType<'bool'>;
export type DateTimeDataType = BaseDataType<'datetime'>;
export type ArrayDataType = BaseDataType<'array', true>;
export type WindowDataType = BaseDataType<'Window'>;
export type BoundingBoxDataType = BaseDataType<'BoundingBox'>;
export type StringDataType = BaseDataType<'str', true>;
export type EmbeddingDataType = BaseDataType<'Embedding', true>;
export type Sequence1DDataType = BaseDataType<'Sequence1D', true, true>;
export type MeshDataType = BaseDataType<'Mesh', true, true>;
export type ImageDataType = BaseDataType<'Image', true, true>;
export type AudioDataType = BaseDataType<'Audio', true, true>;
export type VideoDataType = BaseDataType<'Video', true, true>;
export interface SequenceDataType extends BaseDataType<'Sequence', true> {
    dtype: DataType;
    length?: number;
}
export interface CategoricalDataType extends BaseDataType<'Category'> {
    categories: Record<string, number>;
    invertedCategories: Record<number, string>;
}

export type DataType =
    | UnknownDataType
    | IntegerDataType
    | FloatDataType
    | BooleanDataType
    | StringDataType
    | ArrayDataType
    | DateTimeDataType
    | MeshDataType
    | Sequence1DDataType
    | EmbeddingDataType
    | ImageDataType
    | AudioDataType
    | VideoDataType
    | WindowDataType
    | BoundingBoxDataType
    | CategoricalDataType
    | SequenceDataType;

// type guards
export const isInteger = (type: DataType): type is IntegerDataType =>
    type.kind === 'int';
export const isFloat = (type: DataType): type is FloatDataType => type.kind === 'float';
export const isBoolean = (type: DataType): type is BooleanDataType =>
    type.kind === 'bool';
export const isString = (type: DataType): type is StringDataType => type.kind === 'str';
export const isArray = (type: DataType): type is ArrayDataType => type.kind === 'array';
export const isDateTime = (type: DataType): type is DateTimeDataType =>
    type.kind === 'datetime';
export const isMesh = (type: DataType): type is MeshDataType => type.kind === 'Mesh';
export const isSequence1D = (type: DataType): type is Sequence1DDataType =>
    type.kind === 'Sequence1D';
export const isEmbedding = (type: DataType): type is EmbeddingDataType =>
    type.kind === 'Embedding';
export const isImage = (type: DataType): type is ImageDataType => type.kind === 'Image';
export const isAudio = (type: DataType): type is AudioDataType => type.kind === 'Audio';
export const isVideo = (type: DataType): type is VideoDataType => type.kind === 'Video';
export const isWindow = (type: DataType): type is WindowDataType =>
    type.kind === 'Window';
export const isBoundingBox = (type: DataType): type is BoundingBoxDataType =>
    type.kind === 'BoundingBox';
export const isCategorical = (type: DataType): type is CategoricalDataType =>
    type.kind === 'Category';
export const isSequence = (type: DataType): type is SequenceDataType =>
    type.kind === 'Sequence';
export const isUnknown = (type: DataType): type is UnknownDataType =>
    type.kind === 'Unknown';

// composite helper types and guards
export type NumericalDataType = IntegerDataType | FloatDataType;
export const isNumerical = (type: DataType): type is NumericalDataType =>
    ['int', 'float'].includes(type.kind);

export type ScalarDataType = NumericalDataType | StringDataType | BooleanDataType;
export const isScalar = (type: DataType): type is ScalarDataType =>
    ['int', 'float', 'str', 'bool'].includes(type.kind);

// 'null' values for every datatype
export function getNullValue(kind: DataKind): number | boolean | string | null {
    switch (kind) {
        case 'int':
            return 0;
        case 'float':
            return NaN;
        case 'bool':
            return false;
        case 'str':
            return '';
        default:
            return null;
    }
}

export const unknownDataType: UnknownDataType = {
    kind: 'Unknown',
    lazy: false,
    binary: false,
    optional: true,
};

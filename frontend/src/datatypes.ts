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
    'Unknown',
] as const;
export type DataKind = typeof datakinds[number];

export interface BaseDataType<K extends DataKind> {
    kind: K;
    optional: boolean;
}

// type definitions
export type IntegerDataType = BaseDataType<'int'>;
export type FloatDataType = BaseDataType<'float'>;
export type BooleanDataType = BaseDataType<'bool'>;
export type StringDataType = BaseDataType<'str'>;
export type ArrayDataType = BaseDataType<'array'>;
export type DateTimeDataType = BaseDataType<'datetime'>;
export type MeshDataType = BaseDataType<'Mesh'>;
export type SequenceDataType = BaseDataType<'Sequence1D'>;
export type ImageDataType = BaseDataType<'Image'>;
export type AudioDataType = BaseDataType<'Audio'>;
export type VideoDataType = BaseDataType<'Video'>;
export type WindowDataType = BaseDataType<'Window'>;
export interface CategoricalDataType extends BaseDataType<'Category'> {
    kind: 'Category';
    categories: Record<string, number>;
    invertedCategories: Record<number, string>;
}
export interface EmbeddingDataType extends BaseDataType<'Embedding'> {
    kind: 'Embedding';
    embeddingLength: number;
}
export type UnknownDataType = BaseDataType<'Unknown'>;

export type DataType =
    | UnknownDataType
    | IntegerDataType
    | FloatDataType
    | BooleanDataType
    | StringDataType
    | ArrayDataType
    | DateTimeDataType
    | MeshDataType
    | SequenceDataType
    | EmbeddingDataType
    | ImageDataType
    | AudioDataType
    | VideoDataType
    | WindowDataType
    | CategoricalDataType
    | NumericalDataType
    | ScalarDataType;

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
export const isSequence = (type: DataType): type is SequenceDataType =>
    type.kind === 'Sequence1D';
export const isEmbedding = (type: DataType): type is EmbeddingDataType =>
    type.kind === 'Embedding';
export const isImage = (type: DataType): type is ImageDataType =>
    type.kind === 'Sequence1D';
export const isAudio = (type: DataType): type is AudioDataType => type.kind === 'Audio';
export const isVideo = (type: DataType): type is VideoDataType => type.kind === 'Video';
export const isWindow = (type: DataType): type is WindowDataType =>
    type.kind === 'Window';
export const isCategorical = (type: DataType): type is CategoricalDataType =>
    type.kind === 'Category';
export const isUnknown = (type: DataType): type is UnknownDataType =>
    type.kind === 'Unknown';

// composite helper types and guards
export interface NumericalDataType {
    kind: 'int' | 'float';
}
export const isNumerical = (type: DataType): type is NumericalDataType =>
    ['int', 'float'].includes(type.kind);

export interface ScalarDataType {
    kind: 'int' | 'float' | 'str' | 'bool';
}
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

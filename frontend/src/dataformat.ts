import * as d3 from 'd3';
import moment from 'moment';
import numbro from 'numbro';

import { CategoricalDataType, DataKind, DataType } from './datatypes';
import { ColumnData, DataColumn, IndexArray } from './types';

// format a datatype's kind
export function formatKind(kind: DataKind, plural = false): string {
    switch (kind) {
        case 'float':
            return plural ? 'Floats' : 'Float';
        case 'int':
            return plural ? 'Integers' : 'Integer';
        case 'bool':
            return plural ? 'Booleans' : 'Boolean';
        case 'str':
            return plural ? 'Strings' : 'String';
        case 'array':
            return plural ? 'Arrays' : 'Array';
        case 'datetime':
            return plural ? 'Datetimes' : 'Datetime';
        case 'Mesh':
            return plural ? 'Meshes' : 'Mesh';
        case 'Sequence1D':
            return plural ? 'Sequences' : 'Sequence';
        case 'Embedding':
            return plural ? 'Embeddings' : 'Embedding';
        case 'Image':
            return plural ? 'Images' : 'Image';
        case 'Audio':
            return plural ? 'Sounds' : 'Sound';
        case 'Video':
            return plural ? 'Videos' : 'Video';
        case 'Window':
            return plural ? 'Windows' : 'Window';
        case 'Category':
            return plural ? 'Categoricals' : 'Categorical';
        case 'Unknown':
            return 'Unknown';
    }
}

// format a datatype (either as singular or plural)
export function formatType(type: DataType, plural = false): string {
    return formatKind(type.kind, plural);
}

// can the format function produce a more meaningful representation than '<type>'?
export function canFormat(type: DataType): boolean {
    return ['str', 'int', 'float', 'bool', 'datetime', 'Category'].includes(type.kind);
}

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types, @typescript-eslint/no-explicit-any
export function format(value: any, type: DataType, full = false): string {
    // format a single value by it's DataType (usually taken from column.type)

    if (value === null) {
        return '';
    }

    switch (type.kind) {
        case 'str':
            return value;
        case 'Category':
            return (type as CategoricalDataType).invertedCategories[value];
        case 'int':
            return formatNumber(value);
        case 'float':
            return formatNumber(value, {
                optionalMantissa: false,
                trimMantissa: false,
                ...(!full && { mantissa: 4 }),
            });
        case 'bool':
            return `${value}`;
        case 'datetime':
            if (full) {
                return moment(value).format('YYYY-MM-DD HH:mm:ss.SSSSSS');
            }
            return moment(value).format('llll');
        case 'Window':
            return `[${formatNumber(value[0], {
                optionalMantissa: false,
                trimMantissa: false,
                ...(!full && { mantissa: 4 }),
            })}, ${formatNumber(value[1], {
                optionalMantissa: false,
                trimMantissa: false,
                ...(!full && { mantissa: 4 }),
            })}]`;
        case 'Audio':
        case 'Image':
        case 'Mesh':
        case 'Video':
        case 'Sequence1D':
            return value;
        default:
            return `<${formatType(type)}>`;
    }
}

export function parse(
    text: string,
    type: DataType
): number | string | boolean | null | undefined {
    // parse a single value by it's DataType (usually taken from column.type)
    // returns null for an explicitly missing value
    // returns undefined for malformed input

    if (text === '') return null;

    switch (type.kind) {
        case 'str':
            return text;
        case 'int':
            if (text.toLowerCase() === 'nan') return Number.NaN;
            return numbro.unformat(text);
        case 'float':
            if (text.toLowerCase() === 'nan') return Number.NaN;
            if (['inf', '+inf'].includes(text)) return Infinity;
            if (text === '-inf') return -Infinity;
            return numbro.unformat(text);

        case 'bool':
            return text.toLowerCase() === 'true';
        case 'Category':
            return text === '' ? -1 : type.categories[text];
        case 'Audio':
        case 'Image':
        case 'Mesh':
        case 'Video':
        case 'Sequence1D':
            return text;
        default:
            throw new Error(`Can't parse value of type: ${type.kind}`);
    }
}

export function formatNumber(value: number, options?: numbro.Format): string {
    // return early for NaN values
    // as they break the following mantissa calculation
    if (value === null) return '';
    if (isNaN(value)) return numbro(value).format();

    // parse a number with numbro and return a string
    // format options are guessed but can be overwritten with numbro style in options
    const lg = Math.max(0, Math.floor(Math.log10(Math.abs(value))));

    const formatOptions = {
        average: false,
        mantissa: Math.max(0, 3 - lg),
        trimMantissa: true,
        optionalMantissa: true,
        exponential: true,
    };

    if (Math.abs(value) < 0.001 && value !== 0) {
        formatOptions.mantissa = 2;
    } else if (lg < 4) {
        formatOptions.exponential = false;
    }

    const formatted = numbro(value).format({ ...formatOptions, ...options });

    return formatted;
}

const dataformat = {
    format,
    formatNumber,
    parse,
    canFormat,
    formatType,
    formatKind,
};

type TransferFunction = (val?: number) => number;

const MIN_SIZE = 0.5;
const MAX_SIZE = 1.5;
const constantTransferFunction: TransferFunction = () => 0.75;

export const createSizeTransferFunction = (
    sizeBy: DataColumn | undefined,
    data: ColumnData,
    rowIndices: IndexArray
): TransferFunction => {
    if (sizeBy && ['float', 'int', 'bool'].includes(sizeBy.type.kind)) {
        const sizes = rowIndices
            .map((index) => data[index] as number)
            .filter((value) => !isNaN(value));
        const min = Math.min(...sizes);
        const max = Math.max(...sizes);

        if (min === max) return constantTransferFunction;

        const scale = d3
            .scaleLinear<number | undefined>()
            .domain([min, max])
            .range([MIN_SIZE, MAX_SIZE])
            .unknown(MIN_SIZE);
        return scale as TransferFunction;
    }
    return constantTransferFunction;
};

export default dataformat;

import * as d3 from 'd3';
import moment from 'moment';
import numbro from 'numbro';

import { CategoricalDataType, DataKind, DataType } from '../datatypes';
import { ColumnData, DataColumn, IndexArray } from '../types';
import { AppSettings, Notation, useAppSettings } from '../stores/appSettings';

interface FormatterOptions {
    notation: Notation;
}

export class Formatter {
    notation: Notation;

    constructor(options: FormatterOptions) {
        this.notation = options.notation;
    }

    // can the format function produce a more meaningful representation than '<type>'?
    canFormat(type: DataType): boolean {
        return ['str', 'int', 'float', 'bool', 'datetime', 'Category'].includes(
            type.kind
        );
    }

    // eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types, @typescript-eslint/no-explicit-any
    format(value: any, type: DataType, full = false): string {
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
                return numbro(value).format();
            case 'float':
                return this.formatFloat(value);
            case 'bool':
                return `${value}`;
            case 'datetime':
                if (full) {
                    return moment(value).format('YYYY-MM-DD HH:mm:ss.SSSSSS');
                }
                return moment(value).format('llll');
            case 'Window':
            case 'BoundingBox':
                return (
                    '[' +
                    value.map((x: number) => this.formatFloat(x, full)).join(', ') +
                    ']'
                );
            case 'Audio':
            case 'Image':
            case 'Mesh':
            case 'Video':
            case 'Sequence1D':
            case 'Sequence':
                return value;
            default:
                return `<${formatType(type)}>`;
        }
    }

    formatFloat(value: number, full = false): string {
        // return early for NaN values
        // as they break the following mantissa calculation
        if (value === null) return '';
        if (isNaN(value)) return numbro(value).format();

        const lg = Math.floor(Math.abs(Math.log10(Math.abs(value))));

        const formatOptions = {
            average: false,
            exponential: this.notation === 'scientific' && lg > 1,
            trimMantissa: false,
            optionalMantissa: true,
            ...(!full && { mantissa: 4 }),
        };

        const formatted = numbro(value).format(formatOptions);
        return formatted;
    }
}

let sharedFormatter = new Formatter({ notation: 'scientific' });
const notationSelector = (settings: AppSettings) => settings.numberNotation;

export function useFormatter() {
    const notation = useAppSettings(notationSelector);
    if (sharedFormatter.notation != notation) {
        sharedFormatter = new Formatter({ notation: notation });
    }
    return sharedFormatter;
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
        case 'BoundingBox':
            return plural ? 'BoundingBoxes' : 'BoundingBox';
        case 'Category':
            return plural ? 'Categoricals' : 'Categorical';
        case 'Sequence':
            return plural ? 'Sequences' : 'Sequence';
        case 'Unknown':
            return 'Unknown';
    }
}

// format a datatype (either as singular or plural)
export function formatType(type: DataType, plural = false): string {
    return formatKind(type.kind, plural);
}

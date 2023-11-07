import { DataType } from '../../datatypes';
import _ from 'lodash';
import { Column } from '../../client';
import { DataColumn } from '../../types';

function makeDatatype(
    dtype: NonNullable<Column['dtype']>,
    optional: boolean
): DataType {
    const kind = dtype.name;

    switch (kind) {
        case 'int':
        case 'float':
        case 'bool':
        case 'Window':
        case 'datetime':
        case 'BoundingBox':
            return {
                kind,
                binary: false,
                lazy: false,
                optional: optional,
            };
        case 'str':
        case 'array':
        case 'Embedding':
            return {
                kind,
                binary: false,
                lazy: true,
                optional: optional,
            };
        case 'Image':
        case 'Video':
        case 'Audio':
        case 'Mesh':
        case 'Sequence1D':
            return {
                kind,
                binary: true,
                lazy: true,
                optional: optional,
            };
        case 'Category':
            return {
                kind,
                binary: false,
                lazy: false,
                optional: optional,
                categories: dtype.categories ?? {},
                invertedCategories: _.invert(dtype.categories ?? {}),
            };
        case 'Sequence':
            return {
                kind,
                binary: false,
                lazy: true,
                optional: optional,
                dtype: makeDatatype(dtype.dtype, true),
                length: dtype.length,
            };
    }
    return {
        kind: 'Unknown',
        lazy: false,
        binary: false,
        optional: optional,
    };
}

export function makeColumn(column: Column, index: number): DataColumn {
    const col: DataColumn = {
        index,
        key: column.name,
        name: column.name,
        type: makeDatatype(column.dtype, column.optional),
        editable: column.editable,
        optional: column.optional,
        hidden: column.hidden,
        description: column.description ?? '',
        tags: _.uniq(column.tags),
    };

    return col;
}

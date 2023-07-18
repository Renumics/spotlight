import { DataType } from '../../datatypes';
import _ from 'lodash';
import { Column } from '../../client';
import { DataColumn, isSequence1DColumn, Sequence1DColumn } from '../../types';

function makeDatatype(column: Column): DataType {
    const kind = column.role as DataType['kind'];

    switch (kind) {
        case 'int':
        case 'float':
        case 'str':
        case 'bool':
        case 'Window':
        case 'array':
        case 'datetime':
            return {
                kind,
                binary: false,
                optional: column.optional,
            };
        case 'Image':
        case 'Video':
        case 'Audio':
        case 'Mesh':
        case 'Sequence1D':
            return {
                kind,
                binary: true,
                optional: column.optional,
            };
        case 'Category':
            return {
                kind,
                binary: false,
                optional: column.optional,
                categories: column.categories ?? {},
                invertedCategories: _.invert(column.categories ?? {}),
            };
        case 'Embedding':
            return {
                kind,
                binary: false,
                embeddingLength: column.embeddingLength ?? 0,
                optional: column.optional,
            };
    }
    return {
        kind: 'Unknown',
        binary: false,
        optional: column.optional,
    };
}

export function makeColumn(
    column: Column,
    index: number
): DataColumn | Sequence1DColumn {
    const isInternal = column.name.startsWith('__');
    const type = makeDatatype(column);

    const col: DataColumn = {
        index,
        name: column.name,
        order: column.index ?? 0,
        type: type,
        hidden: column.hidden,
        lazy: column.lazy,
        editable: column.editable,
        optional: column.optional,
        description: column.description,
        isInternal,
        // we access some internal columns like __id__ by their name
        // therefore, if we set the key to something different than column.name
        // we have to check for isInternal and use column.name for it
        key: column.name,
        tags: _.uniq(column.tags),
    };

    if (isSequence1DColumn(col)) {
        col.xLabel = column.xLabel;
        col.yLabel = column.yLabel;
    }

    return col;
}

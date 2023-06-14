import { datakinds, DataType } from '../../datatypes';
import _ from 'lodash';
import { Column } from '../../client';
import { DataColumn, isSequence1DColumn, Sequence1DColumn } from '../../types';

function makeDatatype(column: Column) {
    const kind = column.role as DataType['kind'];

    switch (kind) {
        case 'Category':
            return {
                kind,
                optional: column.optional,
                categories: column.categories ?? {},
                invertedCategories: _.invert(column.categories ?? {}),
            };
        case 'Embedding':
            return {
                kind,
                embeddingLength: column.embeddingLength ?? 0,
                optional: column.optional,
            };
        default:
            return {
                kind: datakinds.includes(kind) ? kind : 'Unknown',
                optional: column.optional,
            };
    }
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
        lazy: !!column.references,
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

import * as datatypes from './datatypes';
import { adjectives, animals, uniqueNamesGenerator } from 'unique-names-generator';

export interface DataColumn {
    order: number;
    index: number;
    name: string;
    type: datatypes.DataType;
    hidden?: boolean;
    lazy: boolean;
    editable: boolean;
    optional: boolean;
    isInternal: boolean;
    description?: string;
    key: string;
    tags?: string[];
}

export interface NumberColumn extends DataColumn {
    type: datatypes.NumericalDataType;
}
export const isNumberColumn = (col: DataColumn): col is NumberColumn =>
    datatypes.isNumerical(col.type);

export interface BooleanColumn extends DataColumn {
    type: datatypes.BooleanDataType;
}
export const isBooleanColumn = (col: DataColumn): col is BooleanColumn =>
    datatypes.isBoolean(col.type);

export interface CategoricalColumn extends DataColumn {
    type: datatypes.CategoricalDataType;
}

export const isCategoricalColumn = (col: DataColumn): col is CategoricalColumn =>
    datatypes.isCategorical(col.type);

export interface ScalarColumn extends DataColumn {
    type: datatypes.ScalarDataType;
}
export const isScalarColumn = (col: DataColumn): col is ScalarColumn =>
    datatypes.isScalar(col.type);

export interface ArrayColumn extends DataColumn {
    type: datatypes.ScalarDataType;
}

export const isArrayColumn = (col: DataColumn): col is ArrayColumn =>
    datatypes.isArray(col.type);

export interface EmbeddingColumn extends DataColumn {
    type: datatypes.EmbeddingDataType;
}

export const isEmbeddingColumn = (col: DataColumn): col is EmbeddingColumn =>
    datatypes.isEmbedding(col.type);

export interface DateColumn extends DataColumn {
    type: datatypes.DateTimeDataType;
}

export const isDateColumn = (col: DataColumn): col is DateColumn =>
    datatypes.isDateTime(col.type);

export interface Sequence1DColumn extends DataColumn {
    type: datatypes.SequenceDataType;
    yLabel?: string;
    xLabel?: string;
}
export const isSequence1DColumn = (col: DataColumn): col is Sequence1DColumn =>
    datatypes.isSequence(col.type);

export interface MeshColumn extends DataColumn {
    type: datatypes.MeshDataType;
}
export const isMeshColumn = (col: DataColumn): col is MeshColumn =>
    datatypes.isMesh(col.type);

export interface ImageColumn extends DataColumn {
    type: datatypes.ImageDataType;
}

export const isImageColumn = (col: DataColumn): col is ImageColumn =>
    datatypes.isImage(col.type);

export interface UnknownColumn extends DataColumn {
    type: datatypes.UnknownDataType;
}

export const isUnknownColumn = (col: DataColumn): col is UnknownColumn =>
    datatypes.isUnknown(col.type);

export interface RowValues {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
}

export interface DataRow {
    index: number;
    values: RowValues;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ColumnData = any[] | Int32Array | Float32Array;
export type TableData = Record<string, ColumnData>;

export interface DataStatistics {
    max: number;
    min: number;
    mean: number;
    p95: number;
    p5: number;
    std: number;
}

export type ColumnsStats = Record<string, DataStatistics | undefined>;

export interface DataFrame {
    columns: DataColumn[];
    length: number;
    data: TableData;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface Predicate<T = any> {
    shorthand: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    compare: (value: any, referenceValue: T) => boolean;
}

export abstract class Filter {
    kind = 'Filter';
    isEnabled = true;
    isInverted = false;

    abstract apply(rowIndex: number, data: TableData): boolean;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export class PredicateFilter<T = any> extends Filter {
    kind: 'PredicateFilter';
    column: DataColumn;
    predicate: Predicate<T>;
    referenceValue: T;

    constructor(column: DataColumn, predicate: Predicate<T>, referenceValue: T) {
        super();
        this.kind = 'PredicateFilter';
        this.column = column;
        this.predicate = predicate;
        this.referenceValue = referenceValue;
    }

    get type(): datatypes.DataType {
        return this.column.type;
    }

    apply(rowIndex: number, data: TableData): boolean {
        return this.predicate.compare(
            data[this.column.key][rowIndex],
            this.referenceValue
        );
    }
}

export class SetFilter extends Filter {
    kind: 'SetFilter';
    rowIndices: Set<number>;
    name: string;

    constructor(rows: number[] | Set<number>, name?: string) {
        super();
        this.kind = 'SetFilter';
        this.rowIndices = new Set(rows);
        this.name =
            name || uniqueNamesGenerator({ dictionaries: [adjectives, animals] });
    }

    static fromMask(mask: boolean[], name?: string): SetFilter {
        const indices = new Set<number>();
        mask.forEach((inMask, i) => {
            if (inMask) {
                indices.add(i);
            }
        });
        return new SetFilter(indices, name);
    }

    apply(rowIndex: number): boolean {
        return this.rowIndices.has(rowIndex);
    }
}

export type TableView = 'full' | 'filtered' | 'selected';

export type Vec2 = [number, number];

export interface Problem {
    type: string;
    title: string;
    detail?: string;
    instance?: string;
}

export type IndexArray = number[] | Int32Array;

export type TypedArray =
    | Int8Array
    | Uint8Array
    | Int16Array
    | Uint16Array
    | Int32Array
    | Uint32Array
    | Uint8ClampedArray
    | Float32Array
    | Float64Array;

export interface BaseLayoutNode {
    kind: string;
}

export interface SplitNode extends BaseLayoutNode {
    kind: 'split';
    weight: number;
    orientation?: 'horizontal' | 'vertical';
    children: ContainerNode[];
}

export interface WidgetNode extends BaseLayoutNode {
    kind: 'widget';
    type: string;
    name?: string;
    config?: Record<string, unknown>;
}

export interface TabNode extends BaseLayoutNode {
    kind: 'tab';
    weight: number;
    children: WidgetNode[];
}

export type ContainerNode = SplitNode | TabNode;
export type LayoutNode = ContainerNode | WidgetNode;

export interface AppLayout {
    orientation?: 'horizontal' | 'vertical';
    children: ContainerNode[];
}

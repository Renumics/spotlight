import * as datatypes from '../datatypes';
import { isString } from '../datatypes';
import { notifyError } from '../notify';
import type { DataColumn, TableData } from './dataset';
import { uniqueNamesGenerator, adjectives, animals } from 'unique-names-generator';

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

        if (isString(column.type)) {
            // as this is a string column try to create a regex from the reference value
            // in order to be able to inform the user when this fails and we are likely going to
            // fallback to a simple string comparison
            try {
                new RegExp(referenceValue as string);
            } catch (e) {
                notifyError(
                    `Couldn't create regex from filter value ${referenceValue}. Falling back to string comparison.`
                );
            }
        }
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

import { produce } from 'immer';
import _ from 'lodash';
import { create } from 'zustand';
import { DataColumn, Vec2 } from '../types';

type Domain = [number, number];

export interface Settings {
    sequence: {
        yAxis: {
            multiple: boolean;
            setMultiple: (multiple: boolean) => void;
            domains: { [key: string]: [number, number] };
            syncDomain: (key: string, domain: Domain) => void;
            unsyncDomain: (key: string) => void;
        };
        xAxis: {
            extents: Vec2;
            setExtents: (ext: Vec2) => void;
            isSynchronized: boolean;
            setIsSynchronized: (value: boolean) => void;
        };
        visibleColumns: Map<DataColumn, boolean>;
        setSelectableColumns: (columns: DataColumn[]) => void;
        setIsColumnVisible: (column: DataColumn, isVisible: boolean) => void;
    };
}

const useSettings = create<Settings>((set) => {
    const prod = (func: (draft: Settings) => void) =>
        set(produce(func) as (state: Settings) => Settings);

    return {
        sequence: {
            yAxis: {
                multiple: false,
                setMultiple: (multiple: boolean) => {
                    prod((d) => {
                        d.sequence.yAxis.multiple = multiple;
                    });
                },
                domains: {},
                syncDomain: (key: string, domain: Domain) => {
                    set((s) => ({
                        sequence: {
                            ...s.sequence,
                            yAxis: {
                                ...s.sequence.yAxis,
                                domains: {
                                    ...s.sequence.yAxis.domains,
                                    [key]: domain,
                                },
                            },
                        },
                    }));
                },
                unsyncDomain: (key: string) => {
                    set((s) => ({
                        sequence: {
                            ...s.sequence,
                            yAxis: {
                                ...s.sequence.yAxis,
                                domains: _.omit(s.sequence.yAxis.domains, key),
                            },
                        },
                    }));
                },
            },
            xAxis: {
                extents: [-Infinity, Infinity],
                setExtents: (ext: Vec2) => {
                    prod((d) => {
                        d.sequence.xAxis.extents = ext;
                    });
                },
                isSynchronized: true,
                setIsSynchronized: (value: boolean) => {
                    prod((d) => {
                        d.sequence.xAxis.isSynchronized = value;
                    });
                },
            },
            visibleColumns: new Map<DataColumn, boolean>(),
            setIsColumnVisible: (column: DataColumn, isVisible: boolean) => {
                prod((d) => {
                    d.sequence.visibleColumns.set(column, isVisible);
                });
            },
            setSelectableColumns: (columns: DataColumn[]) => {
                prod((d) => {
                    columns.forEach(
                        (col) =>
                            d.sequence.visibleColumns.get(col) === undefined &&
                            d.sequence.visibleColumns.set(col, true)
                    );
                });
            },
        },
    };
});

export default useSettings;

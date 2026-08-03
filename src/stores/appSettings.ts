import configService from '../services/config';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SelectionMode } from '../components/shared/Plot/types';

export const notations = ['scientific', 'standard'] as const;
export type Notation = (typeof notations)[number];

export interface AppSettings {
    numberNotation: Notation;
    setNumberNotation: (notation: Notation) => void;
    // the tool used to select points in all plots
    selectionMode: SelectionMode;
    setSelectionMode: (mode: SelectionMode) => void;
}

export const useAppSettings = create<AppSettings>()(
    persist(
        (set) => ({
            numberNotation: 'scientific',
            setNumberNotation: (notation) =>
                set({
                    numberNotation: notation,
                }),
            selectionMode: 'rectangular',
            setSelectionMode: (mode) =>
                set({
                    selectionMode: mode,
                }),
        }),
        {
            name: 'app_settings',
            storage: configService,
        }
    )
);

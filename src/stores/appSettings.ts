import configService from '../services/config';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const notations = ['scientific', 'standard'] as const;
export type Notation = typeof notations[number];

export interface AppSettings {
    numberNotation: Notation;
    setNumberNotation: (notation: Notation) => void;
}

export const useAppSettings = create<AppSettings>()(
    persist(
        (set) => ({
            numberNotation: 'scientific',
            setNumberNotation: (notation) =>
                set({
                    numberNotation: notation,
                }),
        }),
        {
            name: 'app_settings',
            storage: configService,
        }
    )
);

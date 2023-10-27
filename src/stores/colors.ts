import configService from '../services/config';
import {
    CategoricalPalette,
    categoricalPalettesByName,
    ConstantPalette,
    constantPalettesByName,
    ContinuousPalette,
    continuousPalettesByName,
    defaultCategoricalPalette,
    defaultConstantPalette,
    defaultContinuousPalette,
} from '../palettes';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface ColorsState {
    constantPalette: ConstantPalette;
    categoricalPalette: CategoricalPalette;
    continuousPalette: ContinuousPalette;
    robust: boolean;
    continuousInts: boolean;
    continuousCategories: boolean;
    setConstantPalette: (palette?: ConstantPalette) => void;
    setCategoricalPalette: (palette?: CategoricalPalette) => void;
    setContinuousPalette: (palette?: ContinuousPalette) => void;
    setRobust: (robust: boolean) => void;
    setContinuousInts: (continuous: boolean) => void;
    setContinuousCategories: (continuous: boolean) => void;
}

export const useColors = create<ColorsState>()(
    persist(
        (set) => ({
            constantPalette: defaultConstantPalette,
            categoricalPalette: defaultCategoricalPalette,
            continuousPalette: defaultContinuousPalette,
            robust: false,
            continuousInts: false,
            continuousCategories: false,
            setConstantPalette: (palette) => {
                set({ constantPalette: palette ?? defaultConstantPalette });
            },
            setCategoricalPalette: (palette) => {
                set({ categoricalPalette: palette ?? defaultCategoricalPalette });
            },
            setContinuousPalette: (palette) => {
                set({ continuousPalette: palette ?? defaultContinuousPalette });
            },
            setRobust: (robust: boolean) => {
                set({ robust });
            },
            setContinuousInts: (continuousInts: boolean) => {
                set({ continuousInts });
            },
            setContinuousCategories: (continuousCategories: boolean) => {
                set({ continuousCategories });
            },
        }),
        {
            name: 'colors',
            storage: {
                getItem: async (name) => {
                    const str = (await configService.getItem(name)) as string;
                    const state = JSON.parse(str).state;
                    return {
                        state: {
                            ...state,
                            constantPalette:
                                constantPalettesByName[state?.constantPalette] ??
                                defaultConstantPalette,
                            categoricalPalette:
                                categoricalPalettesByName[state?.categoricalPalette] ??
                                defaultCategoricalPalette,
                            continuousPalette:
                                continuousPalettesByName[state?.continuousPalette] ??
                                defaultContinuousPalette,
                        },
                    };
                },
                setItem: async (name, newValue) => {
                    const state = newValue.state;
                    const str = JSON.stringify({
                        state: {
                            ...state,
                            constantPalette:
                                state?.constantPalette?.name ??
                                defaultConstantPalette.name,
                            categoricalPalette:
                                state?.categoricalPalette?.name ??
                                defaultCategoricalPalette.name,
                            continuousPalette:
                                state?.continuousPalette?.name ??
                                defaultContinuousPalette.name,
                        },
                    });
                    await configService.setItem(name, str);
                },
                removeItem: configService.removeItem,
            },
        }
    )
);

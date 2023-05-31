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
    useRobustColorScales: boolean;
    setConstantPalette: (palette?: ConstantPalette) => void;
    setCategoricalPalette: (palette?: CategoricalPalette) => void;
    setContinuousPalette: (palette?: ContinuousPalette) => void;
    setUseRobustColorScales: (useRobust: boolean) => void;
}

export const useColors = create<ColorsState>()(
    persist(
        (set) => ({
            constantPalette: defaultConstantPalette,
            categoricalPalette: defaultCategoricalPalette,
            continuousPalette: defaultContinuousPalette,
            useRobustColorScales: false,
            setConstantPalette: (palette) => {
                set((state) => {
                    return {
                        ...state,
                        constantPalette: palette ?? defaultConstantPalette,
                    };
                });
            },
            setCategoricalPalette: (palette) => {
                set((state) => {
                    return {
                        ...state,
                        categoricalPalette: palette ?? defaultCategoricalPalette,
                    };
                });
            },
            setContinuousPalette: (palette) => {
                set((state) => {
                    return {
                        ...state,
                        continuousPalette: palette ?? defaultContinuousPalette,
                    };
                });
            },
            setUseRobustColorScales: (useRobustColorScales: boolean) => {
                set((state) => {
                    return { ...state, useRobustColorScales };
                });
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

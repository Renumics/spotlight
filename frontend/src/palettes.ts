import chroma from 'chroma-js';
import _ from 'lodash';
import { theme as twTheme } from 'twin.macro';

const NO_DATA = chroma(twTheme`colors.gray.200`);

// note: the return value of the twin.macro theme has an incompatible type but is actually
// replaced by a compatible string for the css colors, hence the complicated type conversion
const themeColors = {
    black: chroma(twTheme('colors.black') as unknown as string),
    white: chroma(twTheme('colors.white') as unknown as string),
    gray: chroma(twTheme('colors.gray.600') as unknown as string),
    red: chroma(twTheme('colors.red.600') as unknown as string),
    yellow: chroma(twTheme('colors.yellow.600') as unknown as string),
    green: chroma(twTheme('colors.green.600') as unknown as string),
    blue: chroma(twTheme('colors.blue.600') as unknown as string),
    purple: chroma(twTheme('colors.purple.600') as unknown as string),
    primary: chroma(twTheme('colors.blue.600') as unknown as string),
};

const MPN65_PALETTE = [
    '377eb8',
    '66a61e',
    '984ea3',
    '00d2d5',
    'ff7f00',
    'af8d00',
    '7f80cd',
    'b3e900',
    'c42e60',
    'a65628',
    'f781bf',
    '8dd3c7',
    'bebada',
    'fb8072',
    '80b1d3',
    'fdb462',
    'fccde5',
    'bc80bd',
    'cf8c00',
    '1b9e77',
    'd95f02',
    'e7298a',
    'e6ab02',
    'a6761d',
    '0097ff',
    '00d067',
    'f43600',
    '4ba93b',
    '5779bb',
    '927acc',
    '97ee3f',
    'bf3947',
    '9f5b00',
    'f48758',
    '8caed6',
    'f2b94f',
    'e43872',
    'd9b100',
    '9d7a00',
    '698cff',
    'd9d9d9',
    '00d27e',
    'd06800',
    '009f82',
    'c49200',
    'cbe8ff',
    'fecddf',
    'c27eb6',
    '8cd2ce',
    'c4b8d9',
    'f883b0',
    'a49100',
    'f48800',
    '27d0df',
    'a04a9b',
];

const SET2_PALETTE = [
    '#66c2a5',
    '#fc8d62',
    '#8da0cb',
    '#e78ac3',
    '#a6d854',
    '#ffd92f',
    '#e5c494',
    '#b3b3b3',
];

const SET3_PALETTE = [
    '#8dd3c7',
    '#ffffb3',
    '#bebada',
    '#fb8072',
    '#80b1d3',
    '#fdb462',
    '#b3de69',
    '#fccde5',
    '#d9d9d9',
    '#bc80bd',
    '#ccebc5',
    '#ffed6f',
];

const SET1_PALETTE = [
    '#e41a1c',
    '#377eb8',
    '#4daf4a',
    '#984ea3',
    '#ff7f00',
    '#ffff33',
    '#a65628',
    '#f781bf',
    '#999999',
];

const TAB10_PALETTE = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',
];

const TAB20_PALETTE = [
    '#1f77b4',
    '#aec7e8',
    '#ff7f0e',
    '#ffbb78',
    '#2ca02c',
    '#98df8a',
    '#d62728',
    '#ff9896',
    '#9467bd',
    '#c5b0d5',
    '#8c564b',
    '#c49c94',
    '#e377c2',
    '#f7b6d2',
    '#7f7f7f',
    '#c7c7c7',
    '#bcbd22',
    '#dbdb8d',
    '#17becf',
    '#9edae5',
];

const IBM_PALETTE = ['#648FFF', '#785EF0', '#DC267F', '#F66102', '#F8B003'];

const WONG_PALETTE = [
    '#000000',
    '#E69F00',
    '#56B4E9',
    '#2B9E73',
    '#F0E441',
    '#2872B2',
    '#D55E00',
    '#CC79A7',
];

interface BasePalette {
    name: string;
    scale: () => chroma.Scale<chroma.Color>;
    kind: string;
}

export interface CategoricalPalette extends BasePalette {
    maxClasses: number;
    kind: 'categorical';
}

export interface ContinuousPalette extends BasePalette {
    kind: 'continuous';
}

export interface ConstantPalette extends BasePalette {
    kind: 'constant';
}

export type Palette = ContinuousPalette | CategoricalPalette | ConstantPalette;

const constantBluePalette: ConstantPalette = {
    name: 'Constant',
    kind: 'constant',
    scale: () => chroma.scale([themeColors.primary]).nodata(NO_DATA).classes(1),
};

const divergingWinter: ContinuousPalette = {
    name: 'Winter',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#0000ff',
                '#000df9',
                '#001af2',
                '#0026ec',
                '#0033e5',
                '#0040df',
                '#004dd9',
                '#005ad2',
                '#0066cc',
                '#0073c5',
                '#008db9',
                '#009ab2',
                '#00a6ac',
                '#00b3a5',
                '#00c09f',
                '#00cd99',
                '#00da92',
                '#00e68c',
                '#00f386',
                '#00ff80',
            ])
            .nodata(NO_DATA),
};

const divergingAutumn: ContinuousPalette = {
    name: 'Autumn',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#ff0000',
                '#ff0d00',
                '#ff1a00',
                '#ff2600',
                '#ff3300',
                '#ff4000',
                '#ff4d00',
                '#ff5a00',
                '#ff6600',
                '#ff7300',
                '#ff8d00',
                '#ff9a00',
                '#ffa600',
                '#ffb300',
                '#ffc000',
                '#ffcd00',
                '#ffda00',
                '#ffe600',
                '#fff300',
                '#ffff00',
            ])
            .nodata(NO_DATA),
};

const divergingSpectral: ContinuousPalette = {
    name: 'Spectral',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#9e0142',
                '#b71d48',
                '#d0394e',
                '#e2514a',
                '#ef6846',
                '#f8844e',
                '#fba25d',
                '#fdbd6e',
                '#fed483',
                '#fee898',
                '#ecf8a2',
                '#d8ef9d',
                '#bde4a0',
                '#9fd8a3',
                '#7ecca5',
                '#60b9a9',
                '#479fb3',
                '#3783ba',
                '#4a69af',
                '#5e4fa2',
            ])
            .nodata(NO_DATA),
};
const viridisPalette: ContinuousPalette = {
    name: 'Viridis',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#440154',
                '#481567',
                '#482677',
                '#453781',
                '#404788',
                '#39568C',
                '#2D708E',
                '#287D8E',
                '#238A8D',
                '#1F968B',
                '#20A387',
                '#29AF7F',
                '#3CBB75',
                '#55C667',
                '#73D055',
                '#95D840',
                '#B8DE29',
                '#DCE319',
                '#FDE725',
            ])
            .nodata(NO_DATA)
            .mode('lab'),
};

const continuousPlasmaPalette: ContinuousPalette = {
    name: 'Plasma',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#0d0887',
                '#460698',
                '#7e03a8',
                '#a52590',
                '#cc4778',
                '#e26e5c',
                '#f89540',
                '#f4c731',
                '#f0f921',
            ])
            .nodata(NO_DATA),
};

const continuousInfernoPalette: ContinuousPalette = {
    name: 'Inferno',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#000004',
                '#290940',
                '#51127c',
                '#84257b',
                '#b73779',
                '#da606d',
                '#fc8961',
                '#fcc390',
                '#fcfdbf',
            ])
            .nodata(NO_DATA),
};

const rainbowPalette: ContinuousPalette = {
    name: 'Rainbow',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#ff0029',
                '#ff5400',
                '#ffd100',
                '#b0ff00',
                '#33ff00',
                '#00ff4b',
                '#00ffc7',
                '#00b9ff',
                '#003bff',
                '#4300ff',
                '#c100ff',
                '#ff00bf',
            ])
            .nodata(NO_DATA),
};

const jetPalette: ContinuousPalette = {
    name: 'jet',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#000080',
                '#0000bd',
                '#0000fa',
                '#0022ff',
                '#0057ff',
                '#008dff',
                '#00c3ff',
                '#0ff8e8',
                '#3affbc',
                '#66ff91',
                '#91ff66',
                '#bcff3a',
                '#e8ff0f',
                '#ffd500',
                '#ffa400',
                '#ff7200',
                '#ff4000',
                '#fa0e00',
                '#bd0000',
                '#800000',
            ])
            .nodata(NO_DATA),
};

const gnuplot2Palette: ContinuousPalette = {
    name: 'gnuplot2',
    kind: 'continuous',
    scale: () =>
        chroma
            .scale([
                '#000000',
                '#000036',
                '#00006b',
                '#0000a1',
                '#0000d7',
                '#0a00ff',
                '#3400ff',
                '#5e00ff',
                '#8801fe',
                '#b21be4',
                '#dc36c9',
                '#ff51ae',
                '#ff6c93',
                '#ff8778',
                '#ffa25d',
                '#ffbc43',
                '#ffd728',
                '#fff20d',
                '#ffff57',
            ])
            .nodata(NO_DATA),
};

const mpn65Palette: CategoricalPalette = {
    name: 'MPN65',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(MPN65_PALETTE)
            .nodata(NO_DATA)
            .domain([0, MPN65_PALETTE.length - 1])
            .classes(MPN65_PALETTE.length),
    maxClasses: MPN65_PALETTE.length,
};

const set1Palette: CategoricalPalette = {
    name: 'Set1',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(SET1_PALETTE)
            .nodata(NO_DATA)
            .domain([0, SET1_PALETTE.length - 1])
            .classes(SET1_PALETTE.length),
    maxClasses: SET1_PALETTE.length,
};

const set2Palette: CategoricalPalette = {
    name: 'Set2',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(SET2_PALETTE)
            .nodata(NO_DATA)
            .domain([0, SET2_PALETTE.length - 1])
            .classes(SET2_PALETTE.length),
    maxClasses: SET2_PALETTE.length,
};

const set3Palette: CategoricalPalette = {
    name: 'Set3',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(SET3_PALETTE)
            .nodata(NO_DATA)
            .domain([0, SET3_PALETTE.length - 1])
            .classes(SET3_PALETTE.length),
    maxClasses: SET3_PALETTE.length,
};

const tab10Palette: CategoricalPalette = {
    name: 'Tab10',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(TAB10_PALETTE)
            .nodata(NO_DATA)
            .domain([0, TAB10_PALETTE.length - 1])
            .classes(TAB10_PALETTE.length),
    maxClasses: TAB10_PALETTE.length,
};

const tab20Palette: CategoricalPalette = {
    name: 'Tab20',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(TAB20_PALETTE)
            .nodata(NO_DATA)
            .domain([0, TAB20_PALETTE.length - 1])
            .classes(TAB20_PALETTE.length),
    maxClasses: TAB20_PALETTE.length,
};

const wongPalette: CategoricalPalette = {
    name: 'ColorBlind8',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(WONG_PALETTE)
            .nodata(NO_DATA)
            .domain([0, WONG_PALETTE.length - 1])
            .classes(WONG_PALETTE.length),
    maxClasses: WONG_PALETTE.length,
};

const ibmPalette: CategoricalPalette = {
    name: 'ColorBlind5',
    kind: 'categorical',
    scale: () =>
        chroma
            .scale(IBM_PALETTE)
            .nodata(NO_DATA)
            .domain([0, IBM_PALETTE.length - 1])
            .classes(IBM_PALETTE.length),
    maxClasses: IBM_PALETTE.length,
};

export const constantPalettes = [constantBluePalette];
export const constantPalettesByName = _.keyBy(constantPalettes, (p) => p.name);

export const categoricalPalettes = [
    mpn65Palette,
    tab10Palette,
    tab20Palette,
    wongPalette,
    ibmPalette,
    set1Palette,
    set2Palette,
    set3Palette,
];
export const categoricalPalettesByName = _.keyBy(categoricalPalettes, (p) => p.name);

export const continuousPalettes = [
    viridisPalette,
    continuousInfernoPalette,
    continuousPlasmaPalette,
    divergingWinter,
    divergingAutumn,
    divergingSpectral,
    jetPalette,
    gnuplot2Palette,
    rainbowPalette,
];

export const continuousPalettesByName = _.keyBy(continuousPalettes, (p) => p.name);

export const palettes = [
    ...continuousPalettes,
    ...categoricalPalettes,
    ...constantPalettes,
];

export const defaultConstantPalette = constantPalettes[0];
export const defaultCategoricalPalette = categoricalPalettes[0];
export const defaultContinuousPalette = continuousPalettes[0];

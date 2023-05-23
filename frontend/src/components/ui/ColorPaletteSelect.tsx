import ColorPalette from './ColorPalette';
import { makeStyles } from './Select/styles';
import { OptionType } from './Select/types';
import { useMemo } from 'react';
import Select, { components } from 'react-select';
import type { OptionProps, SingleValue, SingleValueProps } from 'react-select';
import 'twin.macro';
import { Palette } from '../../palettes';

type PaletteOption<T extends Palette> = OptionType<T>;

const ColorPaletteOption = <T extends Palette>(
    props: OptionProps<PaletteOption<T>, false>
): JSX.Element => {
    const { value } = props.data;

    return (
        <components.Option {...props}>
            <div tw="flex flex-row text-sm">
                <div>{value?.name}</div>
                <div tw="flex-1" />
                {value && <ColorPalette palette={value} />}
            </div>
        </components.Option>
    );
};

const ColorPaletteValue = <T extends Palette>(
    props: SingleValueProps<PaletteOption<T>, false>
): JSX.Element => {
    const { value } = props.data;
    return (
        <components.SingleValue {...props}>
            <div tw="flex flex-row text-sm">
                <div>{value?.name}</div>
                <div tw="flex-1" />
                {value && <ColorPalette palette={value} />}
            </div>
        </components.SingleValue>
    );
};

export interface Props<T extends Palette> {
    applicableColorPalettes: T[];
    colorPalette?: T;
    onChangeColorPalette?: (palette: T | undefined) => void;
}

const ColorPaletteSelect = <T extends Palette>({
    applicableColorPalettes,
    colorPalette,
    onChangeColorPalette,
}: Props<T>): JSX.Element => {
    const changeColorPalette = (option: SingleValue<PaletteOption<T>>) => {
        onChangeColorPalette?.(option?.value);
    };

    const paletteOptions: PaletteOption<T>[] = applicableColorPalettes.map(
        (palette) => ({
            value: palette,
            label: '',
        })
    );

    const labeledValue = useMemo(
        () =>
            colorPalette === undefined ? undefined : { value: colorPalette, label: '' },
        [colorPalette]
    );

    const styles = useMemo(() => makeStyles<T>(), []);

    const menuPortalTarget = document.getElementById('selectMenuRoot');
    if (menuPortalTarget === null) return <></>;

    return (
        <Select<PaletteOption<T>, false>
            components={{ Option: ColorPaletteOption, SingleValue: ColorPaletteValue }}
            options={paletteOptions}
            onChange={changeColorPalette}
            value={labeledValue}
            isSearchable={false}
            styles={styles}
            isDisabled={applicableColorPalettes.length === 0}
            menuPortalTarget={menuPortalTarget}
        />
    );
};

export default ColorPaletteSelect;

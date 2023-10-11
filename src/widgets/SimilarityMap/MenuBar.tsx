import FilterIcon from '../../icons/Filter';
import FilterOffIcon from '../../icons/FilterOff';
import ResetIcon from '../../icons/Reset';
import SettingsIcon from '../../icons/Settings';
import Button from '../../components/ui/Button';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import { Hint } from '../../components/ui/Menu/MultiColumnSelect';
import Select from '../../components/ui/Select';
import { DataType } from '../../datatypes';
import { FunctionComponent, memo, useCallback, useMemo } from 'react';
import { PCANormalization, UmapMetric } from '../../services/data';
import { Dataset, useDataset } from '../../stores/dataset';
import tw from 'twin.macro';
import { DataColumn } from '../../types';
import { shallow } from 'zustand/shallow';
import { PCAParameterMenu } from './PCAParameterMenu';
import { ReductionMethod, reductionMethods } from './types';
import { UmapParameterMenu } from './UmapParameterMenu';

const Styles = tw.div`pl-2 py-0.5 absolute top-0 right-0 items-start flex flex-row-reverse text-sm`;

interface Props {
    colorBy?: string;
    sizeBy?: string;
    placeBy: string[];
    filter: boolean;
    embeddableColumns: string[];
    embeddableColumnsHints?: { [key: string]: Hint };
    reductionMethod: ReductionMethod;
    umapNNeighbors: number;
    umapMetric: UmapMetric;
    umapMinDist: number;
    pcaNormalization: PCANormalization;
    onChangeColorBy: (columnName?: string) => void;
    onChangeSizeBy: (columnName?: string) => void;
    onChangePlaceBy: (columnNames: string[]) => void;
    onChangeFilter: (value: boolean) => void;
    onChangeReductionMethod: (value?: ReductionMethod) => void;
    onChangeUmapNNeighbors: (value: number) => void;
    onChangeUmapMetric: (value?: UmapMetric) => void;
    onChangeUmapMinDist: (value: number) => void;
    onChangePCANormalization: (value?: PCANormalization) => void;
    onReset: () => void;
}

const columnTypeSelector = (d: Dataset): { [key: string]: DataType } =>
    d.columns.reduce((a: { [key: string]: DataType }, c: DataColumn) => {
        a[c.key] = c.type;
        return a;
    }, {});

const SettingsMenu = ({
    colorBy,
    sizeBy,
    placeBy,
    reductionMethod,
    embeddableColumns,
    embeddableColumnsHints,
    umapNNeighbors,
    umapMetric,
    umapMinDist,
    pcaNormalization,
    onChangeColorBy,
    onChangeSizeBy,
    onChangePlaceBy,
    onChangeReductionMethod,
    onChangeUmapNNeighbors,
    onChangeUmapMetric,
    onChangeUmapMinDist,
    onChangePCANormalization,
}: Props) => {
    const columnType = useDataset(columnTypeSelector, shallow);

    const changePlaceBy = useCallback(
        (keys: string[]): void => {
            onChangePlaceBy(keys);
        },
        [onChangePlaceBy]
    );

    const colorableColumns = useMemo(
        () => [
            '',
            ...Object.entries(columnType)
                .filter(([, type]) =>
                    ['int', 'float', 'str', 'bool', 'Category'].includes(type.kind)
                )
                .map(([col]) => col),
        ],
        [columnType]
    );

    const scaleableColumns = useMemo(
        () => [
            '',
            ...Object.entries(columnType)
                .filter(([, type]) => ['int', 'float', 'bool'].includes(type.kind))
                .map(([col]) => col),
        ],
        [columnType]
    );

    const reductionParameterMenu =
        reductionMethod === 'umap' ? (
            <UmapParameterMenu
                umapNNeighbors={umapNNeighbors}
                umapMetric={umapMetric}
                umapMinDist={umapMinDist}
                onChangeUmapNNeighbors={onChangeUmapNNeighbors}
                onChangeUmapMetric={onChangeUmapMetric}
                onChangeUmapMinDist={onChangeUmapMinDist}
            />
        ) : (
            <PCAParameterMenu
                pcaNormalization={pcaNormalization}
                onChangePcaNormalization={onChangePCANormalization}
            />
        );

    return (
        <Menu tw="w-[360px]">
            <Menu.MultiColumnSelect
                title="Place by"
                selectableColumns={embeddableColumns}
                columnHints={embeddableColumnsHints}
                onChangeColumn={changePlaceBy}
                selected={placeBy}
            />
            <Menu.Title>Reduction method</Menu.Title>
            <Menu.Item>
                <Select
                    value={reductionMethod}
                    onChange={onChangeReductionMethod}
                    options={reductionMethods}
                />
            </Menu.Item>
            {reductionParameterMenu}
            <Menu.HorizontalDivider />
            <Menu.Item>
                <Menu.Title>Color By</Menu.Title>
                <Select
                    onChange={onChangeColorBy}
                    options={colorableColumns}
                    value={colorBy}
                />
            </Menu.Item>
            <Menu.Item>
                <Menu.Title>Scale By</Menu.Title>
                <Select
                    onChange={onChangeSizeBy}
                    options={scaleableColumns}
                    value={sizeBy}
                />
            </Menu.Item>
        </Menu>
    );
};

const MenuBar: FunctionComponent<Props> = (props) => {
    const { onReset, filter, onChangeFilter } = props;

    const toggleFilter = () => onChangeFilter(!filter);

    return (
        <Styles>
            <div data-test-tag="similaritymap-settings-dropdown">
                <Dropdown content={<SettingsMenu {...props} />} tooltip="Settings">
                    <SettingsIcon />
                </Dropdown>
            </div>
            <Button onClick={onReset} tooltip="Fit points">
                <ResetIcon />
            </Button>
            <Button
                onClick={toggleFilter}
                tooltip={filter ? 'show unfiltered' : 'hide unfiltered'}
            >
                {filter ? <FilterOffIcon /> : <FilterIcon />}
            </Button>
        </Styles>
    );
};

export default memo(MenuBar);

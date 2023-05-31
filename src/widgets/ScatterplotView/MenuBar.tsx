import FilterIcon from '../../icons/Filter';
import FilterOffIcon from '../../icons/FilterOff';
import ResetIcon from '../../icons/Reset';
import SettingsIcon from '../../icons/Settings';
import Button from '../../components/ui/Button';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import { FunctionComponent, memo } from 'react';
import tw from 'twin.macro';

const MenuBarWrapper = tw.div`pl-2 py-0.5 absolute top-0 right-0 items-start flex flex-row-reverse text-sm`;

interface MenuProps {
    placeableColumns: string[];
    colorableColumns: string[];
    scaleableColumns: string[];
    xAxisColumn?: string;
    yAxisColumn?: string;
    colorBy?: string;
    sizeBy?: string;
    filter: boolean;
    onChangeXAxisColumn: (column: string) => void;
    onChangeYAxisColumn: (column: string) => void;
    onChangeColorBy: (column: string) => void;
    onChangeSizeBy: (column: string) => void;
    onChangeFilter: (filter: boolean) => void;
    onReset: () => void;
}

type Props = MenuProps;

const SettingsMenu = ({
    onChangeXAxisColumn,
    placeableColumns,
    colorableColumns,
    scaleableColumns,
    onChangeColorBy,
    onChangeSizeBy,
    onChangeYAxisColumn,
    sizeBy,
    colorBy,
    xAxisColumn,
    yAxisColumn,
}: Props): JSX.Element => {
    return (
        <Menu tw="w-[360px]">
            <Menu.ColumnSelect
                title="X-Axis Column"
                onChangeColumn={onChangeXAxisColumn}
                selectableColumns={placeableColumns}
                selected={xAxisColumn}
            />
            <Menu.ColumnSelect
                title="Y-Axis Column"
                onChangeColumn={onChangeYAxisColumn}
                selectableColumns={placeableColumns}
                selected={yAxisColumn}
            />
            <Menu.ColumnSelect
                title="Color By"
                onChangeColumn={onChangeColorBy}
                selectableColumns={colorableColumns}
                selected={colorBy}
            />
            <Menu.ColumnSelect
                title="Scale By"
                onChangeColumn={onChangeSizeBy}
                selectableColumns={scaleableColumns}
                selected={sizeBy}
            />
        </Menu>
    );
};

const MenuBar: FunctionComponent<Props> = (props) => {
    const { filter, onChangeFilter } = props;
    const toggleFilter = () => onChangeFilter(!filter);

    return (
        <MenuBarWrapper>
            <Dropdown content={<SettingsMenu {...props} />} tooltip="Settings">
                <SettingsIcon />
            </Dropdown>
            <Button onClick={props.onReset} tooltip="Fit points">
                <ResetIcon />
            </Button>
            <Button
                onClick={toggleFilter}
                tooltip={filter ? 'show unfiltered' : 'hide unfiltered'}
            >
                {filter ? <FilterOffIcon /> : <FilterIcon />}
            </Button>
        </MenuBarWrapper>
    );
};

export default memo(MenuBar);

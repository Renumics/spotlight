import { MorphStyle } from '../../components//GltfViewer';
import ResetIcon from '../../icons/Refresh';
import FitIcon from '../../icons/Reset';
import SettingsIcon from '../../icons/Settings';
import Button from '../../components/ui/Button';
import Dropdown from '../../components/ui/Dropdown';
import Menu from '../../components/ui/Menu';
import Select from '../../components/ui/Select';
import Slider from '../../components/ui/Slider';
import { FunctionComponent } from 'react';
import tw from 'twin.macro';

const Styles = tw.div`px-0.5 py-0.5 absolute top-0 right-0 items-start flex flex-row-reverse`;

interface Props {
    isViewSynced: boolean;
    availableColors: string[];
    availableMorphStyles: readonly MorphStyle[];
    morphStyle: MorphStyle;
    morphScale: number;
    transparency: number;
    colorAttributeName: string;
    showWireframe: boolean;
    onChangeShowWireframe: (enabled: boolean) => void;
    onReset: () => void;
    onFit: () => void;
    onToggleSync: (enabled: boolean) => void;
    onChangeColorAttributeName: (color: string) => void;
    onChangeMorphStyle: (morphStyle: MorphStyle) => void;
    onChangeMorphScale: (value: number) => void;
    onChangeTransparency: (value: number) => void;
}

const MenuBar: FunctionComponent<Props> = ({
    isViewSynced,
    availableColors,
    availableMorphStyles,
    morphStyle,
    morphScale,
    transparency,
    colorAttributeName,
    showWireframe,
    onChangeShowWireframe,
    onReset,
    onFit,
    onToggleSync,
    onChangeColorAttributeName,
    onChangeMorphStyle,
    onChangeMorphScale,
    onChangeTransparency,
}) => {
    const resetView = () => onReset();
    const fitView = () => onFit();

    const selectColor = (attribute?: string | null) =>
        onChangeColorAttributeName(attribute || '');

    const selectMorphStyle = (newMorphStyle?: MorphStyle) =>
        onChangeMorphStyle(newMorphStyle ?? 'loop');

    const content = (
        <Menu>
            <Menu.Title>Color By</Menu.Title>
            <Select
                onChange={selectColor}
                value={colorAttributeName}
                options={[null, ...availableColors]}
            />
            <Menu.Title>Animation</Menu.Title>
            <Select
                onChange={selectMorphStyle}
                value={morphStyle}
                options={availableMorphStyles}
            />
            <Menu.Title>Scale</Menu.Title>
            <Slider
                min={0}
                max={100}
                value={morphScale}
                onChange={onChangeMorphScale}
            />
            <Menu.Title>Transparency</Menu.Title>
            <Slider
                min={0}
                max={0.9}
                step={0.01}
                value={transparency}
                onChange={onChangeTransparency}
            />
            <Menu.Title>Camera</Menu.Title>
            <Menu.Switch value={isViewSynced} onChange={onToggleSync}>
                Synchronize
            </Menu.Switch>
            <Menu.Title>Mesh</Menu.Title>
            <Menu.Switch value={showWireframe} onChange={onChangeShowWireframe}>
                Show Wireframe
            </Menu.Switch>
        </Menu>
    );

    return (
        <Styles>
            <div data-test-tag="meshview-settings-dropdown">
                <Dropdown content={content}>
                    <SettingsIcon />
                </Dropdown>
            </div>
            <Button tooltip={'Reset camera'} onClick={resetView}>
                <ResetIcon />
            </Button>
            <Button tooltip={'Fit mesh'} onClick={fitView}>
                <FitIcon />
            </Button>
        </Styles>
    );
};

export default MenuBar;

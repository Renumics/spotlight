import application from '../application';
import DocsIcon from '../icons/Docs';
import GithubIcon from '../icons/Github';
import HelpIcon from '../icons/Help';
import OpenFolderIcon from '../icons/OpenFolder';
import ColorPaletteIcon from '../icons/ColorPalette';
import NumberIcon from '../icons/Number';
import Button from './ui/Button';
import Dialog from './ui/Dialog';
import Dropdown, { DropdownContext } from './ui/Dropdown';
import Tooltip from './ui/Tooltip';
import Menu from './ui/Menu';
import { useCallback, useContext, useRef, useState } from 'react';
import { useDataset } from '../stores/dataset';
import tw from 'twin.macro';
import FileBrowser from './FileBrowser';
import TourIcon from '../icons/Tour';
import Logo from './Logo';
import MainWalkthrough, {
    Handle as MainWalkthroughRef,
} from './walkthrough/MainWalkthrough';
import { useColors } from '../stores/colors';
import ColorPaletteSelect from './ui/ColorPaletteSelect';
import { categoricalPalettes, continuousPalettes } from '../palettes';
import Select from './ui/Select';
import { Notation, notations, useAppSettings } from '../stores/appSettings';

const NavBar = tw.nav`py-0.5 px-1 bg-gray-200 flex items-center w-full top-0 z-10 border-b border-gray-400`;

const FileBar = () => {
    const filename = useDataset((d) => d.filename);
    const hasTable = !!filename;

    const [isBrowsing, setIsBrowsing] = useState(false);
    const openBrowser = () => setIsBrowsing(true);
    const closeBrowser = () => setIsBrowsing(false);

    const [openCaption, setOpenCaption] = useState('Open');

    const handleSelect = useCallback((path?: string) => {
        setOpenCaption(path?.endsWith('.csv') ? 'Import' : 'Open');
    }, []);

    const openTable = useCallback((path: string) => {
        useDataset.getState().openTable(path);
        closeBrowser();
    }, []);

    return (
        <>
            <Button
                data-tour="fileBrowser"
                onClick={openBrowser}
                disabled={!application.filebrowsingAllowed}
                tw="flex-grow h-6 mx-2 px-1 border border-gray-400 rounded w-full flex flex-row bg-gray-300 justify-start items-center font-bold text-xs divide-gray-400 divide-x hover:(bg-gray-200 text-blue-600) active:hover:(text-midnight-600) disabled:(bg-gray-200 text-gray-700) active:disabled:(text-gray-700)"
            >
                <div tw="px-1 h-full flex items-center">
                    <OpenFolderIcon />
                </div>
                <div tw="h-full flex items-center px-1">{filename}</div>
            </Button>
            <Dialog isVisible={isBrowsing || !hasTable} onClickOutside={closeBrowser}>
                <FileBrowser
                    onOpen={openTable}
                    onSelect={handleSelect}
                    onCancel={closeBrowser}
                    cancellable={hasTable}
                    openCaption={openCaption}
                    extensions={['h5', 'csv', 'parquet', 'feather', 'orc']}
                />
            </Dialog>
        </>
    );
};

const TourButton = ({ onClick }: { onClick: () => void }): JSX.Element => {
    const dropdown = useContext(DropdownContext);

    const handleClick = useCallback(() => {
        onClick();
        dropdown.hide();
    }, [onClick, dropdown]);

    return (
        <Button tw="w-full" onClick={handleClick} tooltip="Restart Tour">
            <div tw="flex flex-row font-normal w-full items-center content-center">
                <TourIcon />
                <span tw="ml-1 text-sm">Tour</span>
            </div>
        </Button>
    );
};

const GitHubButton = (): JSX.Element => (
    <Button tw="w-full" tooltip="GitHub Repository">
        <a
            tw="flex flex-row font-normal w-full items-center content-center"
            href={application.repositoryUrl}
            target="_blank"
            rel="noreferrer"
        >
            <GithubIcon />
        </a>
    </Button>
);

const HelpMenu = (): JSX.Element => {
    const mainWalkthrough = useRef<MainWalkthroughRef>(null);
    const restartTour = useCallback(() => mainWalkthrough.current?.restartTour(), []);

    const content = (
        <Menu tw="p-0 mt-1">
            <Menu.Item>
                <TourButton onClick={restartTour} />
            </Menu.Item>
            <Menu.Item>
                <Button tw="w-full" tooltip="Open Documentation">
                    <a
                        tw="flex flex-row font-normal w-full items-center content-center"
                        href={application.docsUrl}
                        target="_blank"
                        rel="noreferrer"
                    >
                        <DocsIcon />
                        <span tw="ml-1 text-sm">Documentation</span>
                    </a>
                </Button>
            </Menu.Item>
        </Menu>
    );

    return (
        <div data-tour="helpButton" data-test-tag="help-button">
            <Dropdown content={content} tooltip="Help">
                <HelpIcon />
            </Dropdown>
            <MainWalkthrough ref={mainWalkthrough} />
        </div>
    );
};

const ColorMenu = () => {
    const colors = useColors();

    const content = (
        <div tw="flex flex-col w-72 pb-1">
            <Menu>
                <Menu.Title>Continuous Colors</Menu.Title>
                <Menu.Item>
                    <ColorPaletteSelect
                        colorPalette={colors.continuousPalette}
                        applicableColorPalettes={continuousPalettes}
                        onChangeColorPalette={colors.setContinuousPalette}
                    />
                </Menu.Item>
                <Menu.Title>Categorical Colors</Menu.Title>
                <Menu.Item>
                    <ColorPaletteSelect
                        colorPalette={colors.categoricalPalette}
                        applicableColorPalettes={categoricalPalettes}
                        onChangeColorPalette={colors.setCategoricalPalette}
                    />
                </Menu.Item>

                <Menu.Title>Continuous Ints</Menu.Title>
                <Menu.Switch
                    value={colors.continuousInts}
                    onChange={colors.setContinuousInts}
                >
                    Enable
                </Menu.Switch>

                <Menu.Title>Continuous Categories</Menu.Title>
                <Menu.Switch
                    value={colors.continuousCategories}
                    onChange={colors.setContinuousCategories}
                >
                    Enable
                </Menu.Switch>

                <Menu.Title>Robust Coloring</Menu.Title>
                <Menu.Switch value={colors.robust} onChange={colors.setRobust}>
                    Enable
                </Menu.Switch>
            </Menu>
        </div>
    );

    return (
        <Dropdown content={content} tooltip="Colors">
            <ColorPaletteIcon />
        </Dropdown>
    );
};

const NumberMenu = () => {
    const notation = useAppSettings((s) => s.numberNotation);
    const onChangeNotation = (value?: Notation) => {
        if (value) useAppSettings.getState().setNumberNotation(value);
    };

    const content = (
        <div tw="flex flex-col w-72 pb-1">
            <Menu>
                <Menu.Title>Notation</Menu.Title>
                <Menu.Item>
                    <Select
                        options={notations}
                        value={notation}
                        onChange={onChangeNotation}
                    />
                </Menu.Item>
            </Menu>
        </div>
    );

    return (
        <Dropdown content={content} tooltip="Numbers">
            <NumberIcon />
        </Dropdown>
    );
};

const UpgradeButton = (): JSX.Element => {
    return (
        <a href="https://renumics.com/product/pricing" target="_blank" rel="noreferrer">
            <Button tw="text-xs font-bold bg-blue-500 text-white p-1 ml-1 rounded w-auto disabled:bg-gray-200 disabled:hover:bg-gray-200 disabled:text-gray-500 disabled:hover:text-gray-500 hover:bg-green-200 hover:text-white whitespace-nowrap">
                Get PRO
            </Button>
        </a>
    );
};

type AppBarItem = JSX.Element;
export const appBarItems: AppBarItem[] = [<UpgradeButton key="upgradeButton" />];

const AppBar = (): JSX.Element => {
    return (
        <NavBar>
            <div tw="h-full">
                <Logo />
            </div>
            <div tw="flex items-center ml-1 mr-1 font-bold text-midnight-600">
                Spotlight
            </div>
            <Tooltip content={<>{application.edition.name} Edition</>}>
                <div tw="flex items-center h-6 bg-green-200/30 border-green-200 border-2 rounded p-1 text-xs font-bold">
                    {application.edition.shorthand}
                </div>
            </Tooltip>
            <FileBar tw="flex-grow" />
            <div tw="flex items-center">
                <ColorMenu />
                <NumberMenu />
                <HelpMenu />
                <GitHubButton />
                {appBarItems.map((item, i) => (
                    <div key={i}>{item}</div>
                ))}
            </div>
        </NavBar>
    );
};

export default AppBar;

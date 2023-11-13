import GltfViewer, {
    Handle,
    MeshAttribute,
    MorphStyle,
    morphStyles,
} from '../../components/GltfViewer';
import { ViewerState } from '../../components/GltfViewer/GltfViewer';
import { useCallback, useMemo, useRef, useState } from 'react';
import { ColorsState, useColors } from '../../stores/colors';
import tw from 'twin.macro';
import { Lens } from '../../types';
import useSetting from '../../systems/lenses/useSetting';
import MenuBar from './MenuBar';

const Container = tw.div`relative flex flex-col items-center justify-center w-full h-full`;

const palettesSelector = (c: ColorsState) => ({
    categoricalPalette: c.categoricalPalette,
    continuousPalette: c.continuousPalette,
    constantPalette: c.constantPalette,
});

const MeshLens: Lens = ({ values, syncKey }) => {
    const meshData = values[0] as ArrayBuffer;

    const [colorAttributeName, setColorAttributeName] = useSetting(
        'colorAtributeName',
        ''
    );
    const [isSynchronized, setIsSynchronized] = useSetting('isSynchronized', true);
    const [showWireframe, setShowWireframe] = useSetting('showWireframe', false);
    const [transparency, setTransparency] = useSetting('transparency', 0);
    const [morphStyle, setMorphStyle] = useSetting<MorphStyle>('morphStyle', 'loop');
    const [morphScale, setMorphScale] = useSetting('morphScale', 1);

    const [colorAttributeNames, setColorAttributeNames] = useState<string[]>([]);
    const [meshAttributes, setMeshAttributes] = useState<MeshAttribute[]>([]);

    const viewer = useRef<Handle>(null);

    const resetCamera = useCallback(() => {
        viewer.current?.reset();
    }, []);

    const handleOnFit = useCallback(() => {
        viewer.current?.makeSyncReference();
        viewer.current?.fit();
    }, []);

    const palettes = useColors(palettesSelector);

    const colorPalette = useMemo(() => {
        const attribute = meshAttributes.find((a) => a.name === colorAttributeName);

        if (attribute?.type?.kind === 'int') return palettes.categoricalPalette;
        if (attribute?.type?.kind === 'float') return palettes.continuousPalette;
        return palettes.constantPalette;
    }, [meshAttributes, palettes, colorAttributeName]);

    const handleSelectMorphStyle = useCallback(
        (m: MorphStyle) => {
            setMorphStyle(m);
        },
        [setMorphStyle]
    );

    const handleChangeMorphScale = useCallback(
        (value: number) => {
            const unscaledValue = Math.exp(value / 10);
            setMorphScale(unscaledValue);
        },
        [setMorphScale]
    );

    const handleViewerChange = useCallback((state: ViewerState) => {
        setMeshAttributes(state.availableAttributes);
        setColorAttributeNames(
            state.availableAttributes.map((a: MeshAttribute) => a.name)
        );
    }, []);

    const handleOnLoad = useCallback(() => {
        viewer.current?.reset();
    }, []);

    const handleSelectColor = useCallback(
        (attributeName: string) => {
            setColorAttributeName(attributeName);
        },
        [setColorAttributeName]
    );

    const handleToggleSync = useCallback(
        (synced: boolean) => {
            setIsSynchronized(synced);
            viewer.current?.makeSyncReference();
        },
        [setIsSynchronized]
    );

    return (
        <Container>
            {meshData && (
                <GltfViewer
                    ref={viewer}
                    data={meshData}
                    color={colorAttributeName}
                    colorPalette={colorPalette}
                    showWireframe={showWireframe}
                    onChange={handleViewerChange}
                    onLoad={handleOnLoad}
                    sync={isSynchronized}
                    syncKey={syncKey}
                    morphStyle={morphStyle}
                    morphScale={morphScale}
                    transparency={transparency}
                />
            )}

            {
                // Add the menubar as last component, so that it is rendered on top
                // We don't use a z-index for this, because it interferes with the rendering of the contained menus
            }

            <MenuBar
                isViewSynced={isSynchronized}
                availableColors={colorAttributeNames}
                availableMorphStyles={morphStyles}
                morphStyle={morphStyle}
                morphScale={Math.log(morphScale) * 10}
                transparency={transparency}
                colorAttributeName={colorAttributeName}
                showWireframe={showWireframe}
                onChangeShowWireframe={setShowWireframe}
                onReset={resetCamera}
                onFit={handleOnFit}
                onToggleSync={handleToggleSync}
                onChangeColorAttributeName={handleSelectColor}
                onChangeMorphStyle={handleSelectMorphStyle}
                onChangeMorphScale={handleChangeMorphScale}
                onChangeTransparency={setTransparency}
            />
        </Container>
    );
};

MeshLens.kind = 'MeshView';
MeshLens.displayName = '3D Viewer';
MeshLens.dataTypes = ['Mesh'];
MeshLens.defaultHeight = 256;

export default MeshLens;

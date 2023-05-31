import { PerspectiveCamera } from '@react-three/drei';
import { Canvas } from '@react-three/fiber';
import * as React from 'react';
import { useCallback, useEffect, useImperativeHandle, useRef, useState } from 'react';
import * as THREE from 'three';
import { Palette } from '../../palettes';
import CameraControls, { Handle as CameraControlsRef } from './CameraControls';
import GltfScene, { MeshAttribute } from './GltfScene';
import { MorphStyle } from './morphing';

const LIGHT_COLOR = new THREE.Color('rgb(237, 242, 247)');

export interface ViewerState {
    availableAttributes: MeshAttribute[];
}

export interface Props {
    data?: string | ArrayBuffer;
    color?: string;
    onChange?: (state: ViewerState) => void;
    onLoad?: () => void;
    sync?: boolean;
    syncKey?: string;
    morphStyle?: MorphStyle;
    morphScale?: number;
    colorPalette?: Palette;
    showWireframe?: boolean;
    transparency?: number;
}

export interface Handle {
    reset: () => void;
    fit: () => void;
    makeSyncReference: () => void;
}

const GltfViewer: React.ForwardRefRenderFunction<Handle, Props> = (
    {
        data,
        color,
        onChange,
        onLoad,
        sync = false,
        syncKey = 'default',
        morphStyle = 'loop',
        morphScale = 1,
        colorPalette,
        showWireframe = false,
        transparency = 0,
    },
    ref
) => {
    const [availableAttributes, setAvailableAttributes] = useState<MeshAttribute[]>([]);
    const [scene, setScene] = useState<THREE.Object3D>();

    const controls = useRef<CameraControlsRef>(null);
    const camera = useRef<THREE.PerspectiveCamera>(null);

    useEffect(() => {
        onChange?.({ availableAttributes });
    }, [onChange, availableAttributes]);

    useImperativeHandle(ref, () => ({
        reset: () => {
            controls.current?.reset(scene);
        },
        fit: () => {
            console.log('fit');
            if (scene) {
                controls.current?.fit(scene);
            }
        },
        makeSyncReference: () => {
            controls.current?.makeSyncReference();
        },
    }));

    const handleSceneLoad = useCallback(
        (sceneRoot: THREE.Group, attributes: MeshAttribute[]) => {
            // automatically fit object
            controls.current?.fit(sceneRoot);
            setScene(sceneRoot);
            setAvailableAttributes(attributes);
            onLoad?.();
        },
        [onLoad]
    );

    return (
        <Canvas gl={{ antialias: true }}>
            <PerspectiveCamera
                ref={camera}
                makeDefault={true}
                near={10}
                far={2000}
                position={[0, 0, 100]}
            >
                <directionalLight
                    intensity={0.75}
                    position={[0, 0, 0]}
                    color={LIGHT_COLOR}
                />
            </PerspectiveCamera>

            <CameraControls sync={sync} ref={controls} syncKey={syncKey} />
            <ambientLight intensity={0.15} color={LIGHT_COLOR} />
            {data && (
                <GltfScene
                    data={data}
                    colorPalette={colorPalette}
                    colorAttributeName={color}
                    morphStyle={morphStyle}
                    morphScale={morphScale}
                    transparency={transparency}
                    showWireframe={showWireframe}
                    onLoad={handleSceneLoad}
                />
            )}
        </Canvas>
    );
};

export default React.forwardRef(GltfViewer);

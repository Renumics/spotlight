import { useFrame } from '@react-three/fiber';
import { DataType } from '../../datatypes';
import { ReactElement, useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Palette } from '../../palettes';
import { postprocessMesh } from './loading';
import { calculateMorphPosition, MorphStyle } from './morphing';

export interface MeshAttribute {
    name: string;
    type: DataType;
}

export interface Props {
    data: string | ArrayBuffer;
    colorAttributeName?: string;
    morphStyle: MorphStyle;
    morphScale: number;
    transparency?: number;
    colorPalette?: Palette;
    showWireframe?: boolean;
    onLoad?: (scene: THREE.Group, attributes: MeshAttribute[]) => void;
}

// a global clock for synced animations
const globalClock = new THREE.Clock();
globalClock.start();

type TypedArray =
    | Int8Array
    | Uint8Array
    | Int16Array
    | Uint16Array
    | Int32Array
    | Uint32Array
    | Uint8ClampedArray
    | Float32Array
    | Float64Array;

function getTypedArrayDataType(array: TypedArray): DataType {
    switch (array.constructor) {
        case Int8Array:
        case Uint8Array:
        case Int16Array:
        case Uint16Array:
        case Int32Array:
        case Uint32Array:
        case Uint8ClampedArray:
            return { kind: 'int', optional: false, binary: false, lazy: false };
        case Float32Array:
        case Float64Array:
            return { kind: 'float', optional: false, binary: false, lazy: false };
        default:
            return { kind: 'Unknown', optional: false, binary: false, lazy: false };
    }
}

const GltfScene = ({
    data,
    colorAttributeName,
    morphStyle,
    morphScale,
    transparency = 0,
    colorPalette,
    showWireframe = false,
    onLoad,
}: Props): ReactElement => {
    // the scene
    const [scene, setScene] = useState<THREE.Object3D>(() => new THREE.Group());
    // list of current meshes for simpler color changes
    const [meshes, setMeshes] = useState<THREE.Mesh[]>(() => []);

    const sceneRef = useRef<THREE.Object3D>();

    useEffect(() => {
        try {
            new GLTFLoader().parse(data, '/', (result) => {
                // stop here if component is already unmounted
                if (!sceneRef.current) return;

                const newMeshes: THREE.Mesh[] = [];
                const attributes = new Set<MeshAttribute>();

                const parsedScene = result.scene;

                parsedScene.traverse((node: THREE.Object3D) => {
                    if (node instanceof THREE.Mesh) {
                        // perform our custom postprocessing
                        postprocessMesh(node);

                        // find all colorable user attributes (prefixed with '_' and scalar) to pass them in onLoad
                        const geometry = node.geometry as THREE.BufferGeometry;

                        Object.entries(geometry.attributes)
                            .filter(([key, attribute]) => {
                                return key.startsWith('_') && attribute.itemSize === 1;
                            })
                            .forEach(([attributeName, attribute]) => {
                                // add the attribute's name without the leading underscore
                                // and the deduced datatype assuming that the gltf loader always stores them as typedarrays
                                const attributeType = getTypedArrayDataType(
                                    (attribute as THREE.BufferAttribute)
                                        .array as TypedArray
                                );
                                attributes.add({
                                    name: attributeName.substring(1),
                                    type: attributeType,
                                });
                            });

                        // add mesh to list of meshes for faster access during animation
                        newMeshes.push(node);
                    }
                });

                const sceneBounds = new THREE.Box3();
                sceneBounds.setFromObject(parsedScene);
                const center = new THREE.Vector3();
                sceneBounds.getCenter(center);

                parsedScene.position.sub(center);

                setMeshes(newMeshes);
                setScene(parsedScene);
                onLoad?.(parsedScene, Array.from(attributes));
            });
        } catch (e) {
            // silently suppress parsing errors for now
        }
    }, [data, onLoad]);

    useEffect(() => {
        const attributeName = `_${colorAttributeName}`;

        for (const mesh of meshes) {
            const geometry = mesh.geometry as THREE.BufferGeometry;
            const material = mesh.material as THREE.MeshStandardMaterial;

            if (attributeName in geometry.attributes && colorPalette !== undefined) {
                const colorScale = colorPalette.scale();

                const attribute = geometry.attributes[
                    attributeName
                ] as THREE.BufferAttribute;
                const colorAttribute = new THREE.BufferAttribute(
                    new Float32Array(attribute.count * 3),
                    3,
                    true
                );

                let minValue = Number.POSITIVE_INFINITY;
                let maxValue = Number.NEGATIVE_INFINITY;
                for (let i = 0; i < attribute.count; ++i) {
                    const value = attribute.getX(i);
                    if (value > maxValue) maxValue = value;
                    if (value < minValue) minValue = value;
                }

                if (colorPalette.kind === 'categorical') {
                    for (let i = 0; i < attribute.count; ++i) {
                        const value = attribute.getX(i);

                        const color = colorScale(value % colorPalette.maxClasses).gl();

                        colorAttribute.setXYZ(i, color[0], color[1], color[2]);
                    }
                } else {
                    for (let i = 0; i < attribute.count; ++i) {
                        const value = attribute.getX(i);

                        // if all values are the same (max === min), the usual calculation breaks.
                        // Just apply the color for zero in that case.
                        const at =
                            minValue === maxValue
                                ? 0
                                : value - minValue / (maxValue - minValue);
                        const color = colorScale(at).gl();

                        colorAttribute.setXYZ(i, color[0], color[1], color[2]);
                    }
                }

                geometry.attributes.color = colorAttribute;
                material.vertexColors = true;
            } else {
                material.vertexColors = false;
            }

            material.needsUpdate = true;
        }
    }, [colorAttributeName, meshes, colorPalette]);

    useEffect(() => {
        for (const mesh of meshes) {
            const material = mesh.material as THREE.MeshStandardMaterial;
            material.transparent = transparency > 0;
            material.opacity = 1.0 - transparency;
            material.needsUpdate = true;
        }
    }, [transparency, meshes]);

    useEffect(() => {
        for (const mesh of meshes) {
            const material = mesh.material as THREE.MeshStandardMaterial;
            material.wireframe = showWireframe;
        }
    }, [showWireframe, meshes]);

    useFrame(() => {
        for (const mesh of meshes) {
            // update morph target influences
            if (mesh.morphTargetInfluences) {
                const targetCount = mesh.morphTargetInfluences?.length + 1;

                // reset all morph target influences to zero
                mesh.morphTargetInfluences.fill(0);

                // determine current interpolation position
                const duration = 2.0;
                const at =
                    calculateMorphPosition(
                        globalClock.getElapsedTime() / duration,
                        morphStyle
                    ) *
                    (targetCount - 1);

                // lerp between the two closest morph targets
                const sign = Math.sign(at);
                const a = Math.floor(Math.abs(at));

                const b = (a + 1) % targetCount;
                const t = Math.abs(at) % 1;

                if (a > 0)
                    mesh.morphTargetInfluences[a - 1] = sign * morphScale * (1 - t);
                if (b > 0) mesh.morphTargetInfluences[b - 1] = sign * morphScale * t;
            }
        }
    });

    return <primitive ref={sceneRef} dispose={null} object={scene} />;
};

export default GltfScene;

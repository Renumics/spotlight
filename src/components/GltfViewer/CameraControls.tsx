import { TrackballControls } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as React from 'react';
import {
    ComponentRef,
    useCallback,
    useEffect,
    useImperativeHandle,
    useRef,
    useState,
} from 'react';
import * as THREE from 'three';

interface SharedState {
    [syncKey: string]: {
        target: THREE.Vector3;
        position: THREE.Vector3;
        up: THREE.Vector3;
        zoom: number;
    };
}
const sharedState: SharedState = {};

type ValidCamera = THREE.PerspectiveCamera;
const masterControls: Record<
    string,
    ComponentRef<typeof TrackballControls> | undefined
> = {};

export interface Props {
    target?: THREE.Vector3;
    sync?: boolean;
    syncKey?: string;
}

interface ExtraMethods {
    reset: (fitTo?: THREE.Object3D) => void;
    fit: (object: THREE.Object3D, offset?: number) => void;
    makeSyncReference: () => void;
}
export type Handle = ExtraMethods;

const CameraControls: React.ForwardRefRenderFunction<Handle, Props> = (
    { target, sync = false, syncKey = 'default' },
    ref
) => {
    const [controls, setControls] = useState<ComponentRef<typeof TrackballControls>>();
    const isFirstFrame = useRef(true);

    const handleControlsChange = useCallback(
        (controlsRef: ComponentRef<typeof TrackballControls> | null) => {
            if (!controlsRef) return;
            if (controls === masterControls[syncKey]) {
                masterControls[syncKey] = controlsRef;
            }
            setControls(controlsRef);
        },
        [controls, syncKey]
    );

    const fit = (object: THREE.Object3D, offset = 1.0) => {
        if (!controls) return;

        if (sync && !masterControls[syncKey]) {
            masterControls[syncKey] = controls;
        }

        const cam = controls.object as ValidCamera;

        const bounds = new THREE.Box3().setFromObject(object);
        const center = bounds.getCenter(new THREE.Vector3());
        const size = bounds.getSize(new THREE.Vector3());

        const fov = (Math.PI * cam.fov) / 360;

        const distance =
            cam.aspect > size.x / size.y
                ? size.y / (4 * Math.tan(fov / 2)) + size.z / 2
                : size.x / (4 * Math.tan(fov / 2) * cam.aspect) + size.z / 2;

        controls.maxDistance = distance * 10;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (controls as any).target = center.clone();

        cam.near = distance / 100;
        cam.far = distance * 100;
        cam.updateProjectionMatrix();

        const direction = center
            .clone()
            .sub(cam.position)
            .normalize()
            .multiplyScalar(offset * distance);

        cam.position.copy(center).sub(direction);

        controls.update?.();
    };

    useImperativeHandle(ref, () => ({
        ...controls,
        reset: (fitTo?: THREE.Object3D) => {
            if (sync && masterControls[syncKey] && masterControls[syncKey] !== controls)
                return;

            if (sync) {
                masterControls[syncKey] = controls;
            }

            controls?.reset?.();
            if (fitTo) {
                fit(fitTo);
            }
        },
        fit,
        makeSyncReference: () => {
            masterControls[syncKey] = controls;
        },
    }));

    useEffect(() => {
        if (!sync) return;

        if (!masterControls[syncKey]) {
            masterControls[syncKey] = controls;
        }

        const onStart = () => {
            masterControls[syncKey] = controls;
        };

        controls?.addEventListener?.('start', onStart);

        return () => {
            if (masterControls[syncKey] === controls) {
                masterControls[syncKey] = undefined;
            }
            controls?.removeEventListener?.('start', onStart);
        };
    }, [sync, syncKey, controls]);

    useFrame(() => {
        if (!controls) return;

        const cam = controls.object as ValidCamera | undefined;
        const isMaster = masterControls[syncKey] === controls;
        const hasSharedState = !!sharedState[syncKey];

        if (
            sync &&
            (!isMaster || isFirstFrame.current) &&
            cam?.position &&
            hasSharedState
        ) {
            const shared = sharedState[syncKey];
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const t = (controls as any).target as THREE.Vector3;
            t.copy(shared.target as THREE.Vector3);

            cam.position.copy(shared.position);
            cam.up.copy(shared.up);
            cam.zoom = shared.zoom;
            cam.updateProjectionMatrix();
            cam.lookAt(t);
            controls.update?.();
        }

        if (sync && isMaster && cam?.position) {
            if (!hasSharedState) {
                sharedState[syncKey] = {
                    target: new THREE.Vector3(0, 0, 0),
                    position: new THREE.Vector3(0, 0, 1),
                    up: new THREE.Vector3(0, 1, 0),
                    zoom: 0,
                };
            }
            const shared = sharedState[syncKey];

            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            shared.target.copy((controls as any).target as THREE.Vector3);
            shared.position.copy(cam.position);
            shared.up.copy(cam.up);
            shared.zoom = cam.zoom;
        }

        isFirstFrame.current = false;
    });

    return <TrackballControls ref={handleControlsChange} target={target} />;
};

export default React.forwardRef(CameraControls);

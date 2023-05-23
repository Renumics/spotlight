import { useEffect } from 'react';
import { isWebGLAvailable } from 'three-stdlib';
import { useMessages } from '../../stores/messages';

const WebGLDetector = (): null => {
    useEffect(() => {
        if (!isWebGLAvailable()) {
            useMessages
                .getState()
                .addPersistentWarning(
                    'Missing WebGL support! Check if WebGL is enabled in your browser.'
                );
        }
    }, []);

    return null;
};

export default WebGLDetector;

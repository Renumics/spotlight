import useResizeObserver from '@react-hook/resize-observer';
import { useRef } from 'react';
import { Cropper } from 'react-cropper';
import type { ReactCropperElement } from 'react-cropper';
import tw, { styled } from 'twin.macro';
import { View } from '../types';
import MenuBar from './MenuBar';

import 'cropperjs/dist/cropper.css';

const Container = tw.div`
    flex relative flex-col items-center justify-center w-full h-full
`;

const StyledCropper = styled(Cropper)`
    ${tw`h-full w-full`}
`;

// Cropper does not have 'onResize' by default,
// it is dynamically bound when 'responsive' is set.
interface ResponsiveCropper extends Cropper {
    onResize?: () => void;
}

const ImageView: View = ({ url }) => {
    const viewer = useRef<ReactCropperElement>(null);
    const container = useRef<HTMLDivElement>(null);

    useResizeObserver(container.current, () => {
        const cropper = viewer?.current?.cropper;

        (cropper as ResponsiveCropper)?.onResize?.();
    });

    const resetImage = () => {
        const cropper = viewer?.current?.cropper;

        cropper?.reset();
    };

    const rotateImage = () => {
        const cropper = viewer?.current?.cropper;

        cropper?.rotate(90);
    };

    return (
        <Container ref={container}>
            <StyledCropper
                src={url}
                // Cropper.js options
                guides={false}
                ref={viewer}
                dragMode="move"
                autoCrop={false}
                minContainerHeight={1}
                minContainerWidth={1}
                viewMode={2}
                toggleDragModeOnDblclick={false}
                background={false}
                responsive={true}
                restore={false}
            />
            <MenuBar onReset={resetImage} onRotate={rotateImage} />
        </Container>
    );
};

ImageView.dataTypes = ['Image'];
ImageView.displayName = 'Image';
ImageView.defaultHeight = 256;

export default ImageView;

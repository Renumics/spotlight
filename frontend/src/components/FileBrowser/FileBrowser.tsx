import { FileEntry } from '../../client/models/FileEntry';
import { Folder } from '../../client/models/Folder';
import Tour from '../../icons/Tour';
import Button from '../ui/Button';
import FileBrowserWalkthrough, {
    Handle as FileBrowserWalkthroughRef,
} from '../walkthrough/FileBrowserWalkthrough';
import { useCallback, useEffect, useRef, useState } from 'react';
import 'twin.macro';
import api from '../../api';
import { notifyAPIError } from '../../notify';
import AddressBar from './AddressBar';
import { Container, Content, Footer, Header } from './elements';
import FileList from './FileList';

interface Props {
    extensions?: string[];
    cancellable?: boolean;
    openCaption?: string;
    onSelect?: (path?: string) => void;
    onOpen?: (path: string) => void;
    onCancel?: () => void;
}

const TourButton = ({ restartTour }: { restartTour: () => void }) => {
    return (
        <div tw="flex items-center mr-1">
            <Button onClick={restartTour} tooltip="restart tour">
                <Tour />
            </Button>
        </div>
    );
};

const FileBrowser = ({
    onSelect,
    onOpen,
    onCancel,
    openCaption = 'Open',
    extensions,
    cancellable,
}: Props): JSX.Element => {
    const [path, setPath] = useState<string>('.');
    const [folder, setFolder] = useState<Folder>();
    const [selectedFile, setSelectedFile] = useState<FileEntry>();

    const fileBrowserWalkthroughRef = useRef<FileBrowserWalkthroughRef>(null);

    useEffect(() => {
        (async () => {
            try {
                const folder = await api.filebrowser.getFolder({ path });
                setFolder(folder);
            } catch (e) {
                notifyAPIError(e);
            }
        })();
    }, [path]);

    const handleSelectFile = useCallback(
        (entry?: FileEntry) => {
            setSelectedFile(entry);
            onSelect?.(entry?.path);
        },
        [onSelect]
    );

    const openSelectedFile = useCallback(() => {
        if (!selectedFile) return;
        onOpen?.(selectedFile.path);
    }, [selectedFile, onOpen]);

    const restartTour = useCallback(
        () => fileBrowserWalkthroughRef.current?.restartTour(),
        []
    );

    return (
        <Container data-tour="openTableFileDialog">
            <Header>
                <span tw="flex-grow">Open Table File</span>
                <TourButton restartTour={restartTour} />
                <FileBrowserWalkthrough ref={fileBrowserWalkthroughRef} />
            </Header>
            <Content>
                <AddressBar path={path} setPath={setPath} parent={folder?.parent} />
                <FileList
                    setPath={setPath}
                    folder={folder}
                    extensions={extensions}
                    selectedFile={selectedFile}
                    onOpen={onOpen}
                    onSelectFile={handleSelectFile}
                />
            </Content>
            <Footer>
                <Button
                    tw="bg-green-400 text-white disabled:bg-gray-400 disabled:text-gray-700 rounded px-1 py-0.5"
                    onClick={openSelectedFile}
                    disabled={!(selectedFile?.type === 'file')}
                >
                    {openCaption}
                </Button>
                {cancellable && (
                    <Button
                        tw="rounded px-1 py-0.5 font-normal mr-1"
                        onClick={onCancel}
                    >
                        Cancel
                    </Button>
                )}
            </Footer>
        </Container>
    );
};

export default FileBrowser;

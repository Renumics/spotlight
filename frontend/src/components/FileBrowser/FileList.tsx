import { FileEntry } from '../../client/models/FileEntry';
import { Folder } from '../../client/models/Folder';
import FileIcon from '../../icons/File';
import FolderIcon from '../../icons/Folder';
import _ from 'lodash';
import { MouseEvent, useCallback, useEffect, useMemo } from 'react';
import tw from 'twin.macro';

interface Props {
    setPath: (path: string) => void;
    folder?: Folder;
    extensions?: string[];
    onOpen?: (path: string) => void;
    selectedFile?: FileEntry;
    onSelectFile?: (file?: FileEntry) => void;
}

const FileList = ({
    setPath,
    folder,
    extensions,
    onOpen,
    onSelectFile,
    selectedFile,
}: Props): JSX.Element => {
    const visibleFiles = useMemo(() => {
        // filter and sort files
        const filtered =
            folder?.files.filter((f) => {
                if (!extensions || f.type === 'folder') return true;

                const extension = f.name.split('.').pop() ?? '';
                return extensions.includes(extension);
            }) ?? [];
        return _.orderBy(filtered, ['type', 'name'], ['desc', 'asc']);
    }, [folder, extensions]);

    // reset selection when we navigate to another folder
    useEffect(() => {
        onSelectFile?.();
    }, [folder, onSelectFile]);

    const handleFileClick = useCallback(
        (event: MouseEvent<HTMLButtonElement>) => {
            const rawIndex = event.currentTarget.getAttribute('data-index');
            if (rawIndex === null) return;
            const index = parseInt(rawIndex, 10);

            const clickCount = event.detail;
            const file = visibleFiles[index];

            if (clickCount === 1) {
                onSelectFile?.(file);
            } else if (clickCount === 2) {
                if (file?.type === 'folder') {
                    setPath(file.path);
                } else {
                    onOpen?.(file.path);
                }
            }
        },
        [visibleFiles, onOpen, setPath, onSelectFile]
    );

    return (
        <div tw="flex-grow overflow-y-auto bg-white">
            {visibleFiles.map((file, index) => (
                <button
                    onClick={handleFileClick}
                    data-index={index}
                    key={file.name}
                    css={[
                        tw`flex flex-row items-center p-1 cursor-pointer w-full`,
                        file === selectedFile && tw`bg-blue-200`,
                    ]}
                >
                    {file.type === 'file' ? (
                        <FileIcon tw="mr-1 text-gray-800" />
                    ) : (
                        <FolderIcon tw="mr-1 text-gray-800" />
                    )}
                    {file.name}
                </button>
            ))}
        </div>
    );
};

export default FileList;

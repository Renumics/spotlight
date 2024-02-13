import AppBar from './components/AppBar';
import LoadingIndicator from './components/LoadingIndicator';
import StatusBar from './components/StatusBar';
import ToolBar from './components/ToolBar';
import { ContextMenuProvider } from './components/ui/ContextMenu';
import WebGLDetector from './components/WebGLDetector';
import Workspace, { Handle as WorkspaceHandle } from './components/Workspace';
import { useEffect, useRef } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Dataset, useDataset } from './stores/dataset';
import tw from 'twin.macro';
import 'styled-components';
import usePluginStore from './stores/pluginStore';
import DragContext from './systems/dnd/DragContext';
import LoadingError from './components/LoadingError';

const Wrapper = tw.main`bg-gray-200 text-midnight-600 w-screen h-screen relative overflow-hidden`;

// fetch the dataset once on app init
useDataset.getState().fetch();

const loadingSelector = (d: Dataset) => d.loading;
const loadingErrorSelector = (d: Dataset) => d.loadingError;

const App = (): JSX.Element => {
    const plugins = usePluginStore((state) => state.plugins);
    const loading = useDataset(loadingSelector) || plugins === undefined;
    const loadingError = useDataset(loadingErrorSelector);

    const workspace = useRef<WorkspaceHandle>(null);
    const resetWorkspace = () => workspace.current?.reset();
    const saveLayout = () => workspace.current?.saveLayout();
    const loadLayout = (file: File) => workspace.current?.loadLayout(file);

    const filename = useDataset((d) => d.filename);
    useEffect(() => {
        if (filename) {
            document.title = `Spotlight (${filename})`;
        } else {
            document.title = 'Spotlight';
        }
    }, [filename]);

    return (
        <DragContext>
            <Wrapper>
                <WebGLDetector />
                {!loading && !loadingError && (
                    <ContextMenuProvider>
                        <div tw="flex flex-col h-full w-full">
                            <div tw="flex-initial relative">
                                <AppBar />
                            </div>
                            <div tw="flex-initial relative border-b border-gray-400">
                                <ToolBar
                                    resetWorkspace={resetWorkspace}
                                    saveLayout={saveLayout}
                                    loadLayout={loadLayout}
                                />
                            </div>
                            <div tw="flex-grow relative">
                                <Workspace ref={workspace} />
                            </div>
                            <StatusBar />
                        </div>
                    </ContextMenuProvider>
                )}
                {loading && (
                    <div
                        data-test-tag="global-loading-indicator"
                        tw="absolute z-10 w-full h-full left-0 top-0 bg-gray-100"
                    >
                        <LoadingIndicator />
                    </div>
                )}
                {loadingError && <LoadingError problem={loadingError} />}
                <ToastContainer position="bottom-right" />
            </Wrapper>
        </DragContext>
    );
};

export default App;

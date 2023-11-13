import XIcon from '../../../icons/X';
import SettingsIcon from '../../../icons/Settings';
import Button from '../../../components/ui/Button';
import Tooltip from '../../../components/ui/Tooltip';
import { CSSProperties, FunctionComponent, useCallback, useContext } from 'react';
import { Draggable } from 'react-beautiful-dnd';
import type { DraggableProvided } from 'react-beautiful-dnd';
import type { ListChildComponentProps as RowProps } from 'react-window';
import { Dataset, useDataset } from '../../../stores/dataset';
import tw, { styled } from 'twin.macro';
import { shallow } from 'zustand/shallow';
import { RowHeightContext } from '../rowHeightContext';
import { State as StoreState, useStore } from '../store';
import { Dropdown } from '../../../lib';
import MenuFactory from '../../../systems/lenses/MenuFactory';

const RowItemWrapper = styled.div(({ isDropped = false }: { isDropped?: boolean }) => [
    tw`flex flex-col items-center border-b border-r border-gray-400 bg-gray-100 overflow-hidden`,
    isDropped && tw`border-none shadow`,
]);

const ViewNameWrapper = styled.div`
    ${tw`flex-grow flex pb-1 w-full h-full text-xs overflow-hidden`}
    > div {
        ${tw`flex flex-row h-full w-full items-stretch place-content-around`}
    }
`;
const ViewName = styled.span`
    writing-mode: vertical-rl;
    ${tw`transform -rotate-180 truncate`}
`;

const RowFactory: FunctionComponent<RowProps> = ({ index: listIndex, ...props }) => {
    const index = Math.floor(listIndex / 2);

    switch (listIndex % 2) {
        case 0:
            return <Row index={index} {...props} />;
        default:
            return <RowResizer index={index} {...props} />;
    }
};

const RowResizer: FunctionComponent<RowProps> = ({ index, style }) => {
    const { top } = style;

    const { startResize } = useContext(RowHeightContext);

    const onMouseDown = useCallback(
        (event: React.MouseEvent<HTMLDivElement>) => {
            startResize(index, event.screenY);
        },
        [index, startResize]
    );

    return (
        // eslint-disable-next-line jsx-a11y/no-static-element-interactions
        <div
            onMouseDown={onMouseDown}
            tw="transition-colors hover:bg-gray-500 w-full relative"
            css={{ cursor: 'row-resize' }}
            style={{ ...style, height: 3, top: ((top as number) || 0) - 2, zIndex: 1 }}
        ></div>
    );
};

const Row: FunctionComponent<RowProps> = ({ index, style }) => {
    const viewSelector = useCallback(
        (state: StoreState) => state.lenses[index],
        [index]
    );
    const view = useStore(viewSelector);
    return (
        <Draggable index={index} draggableId={view.key} key={view.key}>
            {(provided: DraggableProvided) => (
                <DroppableRowItem index={index} style={style} provided={provided} />
            )}
        </Draggable>
    );
};

type DroppableItemProps = {
    index: number;
    style: CSSProperties;
    provided: DraggableProvided;
    isDropped?: boolean;
};

export const DroppableRowItem: FunctionComponent<DroppableItemProps> = ({
    provided,
    index,
    style,
    isDropped,
}) => {
    return (
        <RowItemWrapper
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            ref={provided.innerRef}
            style={{
                ...style,
                ...provided.draggableProps.style,
            }}
            isDropped={isDropped}
        >
            <RowItem index={index} />
        </RowItemWrapper>
    );
};

type ItemProps = {
    index: number;
};

const removeViewSelector = (state: StoreState) => state.removeLens;

const RowItem: FunctionComponent<ItemProps> = ({ index }) => {
    const viewSelector = useCallback(
        (state: StoreState) => state.lenses[index],
        [index]
    );
    const view = useStore(viewSelector);
    const removeView = useStore(removeViewSelector);

    const columnNamesSelector = useCallback(
        (d: Dataset) =>
            d.columns
                .filter(({ key }) => view.columns.includes(key))
                .map(({ name }) => name)
                .join(),
        [view.columns]
    );
    const columnNames = useDataset(columnNamesSelector, shallow);

    const viewName =
        (!view?.name || view?.name === 'view') && columnNames
            ? columnNames
            : view?.name;
    const longViewName =
        viewName === columnNames || !viewName || !columnNames
            ? viewName
            : `${viewName} (${columnNames})`;

    const onRemoveView = useCallback(
        () => view && removeView(view),
        [removeView, view]
    );

    return (
        <>
            <Button onClick={onRemoveView}>
                <XIcon />
            </Button>
            <Dropdown
                content={
                    <MenuFactory
                        settings={{ foo: { value: 5 } }}
                        onChange={() => null}
                    />
                }
            >
                <SettingsIcon />
            </Dropdown>
            <ViewNameWrapper>
                <Tooltip content={longViewName} followCursor={true}>
                    <ViewName>{viewName}</ViewName>
                </Tooltip>
            </ViewNameWrapper>
        </>
    );
};

export default RowFactory;

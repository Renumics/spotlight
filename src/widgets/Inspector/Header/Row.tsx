import { useSortable } from '@dnd-kit/react/sortable';
import XIcon from '../../../icons/X';
import Button from '../../../components/ui/Button';
import Tooltip from '../../../components/ui/Tooltip';
import {
    CSSProperties,
    forwardRef,
    FunctionComponent,
    HTMLAttributes,
    MouseEvent,
    useCallback,
    useContext,
} from 'react';
import type { ListChildComponentProps as RowProps } from 'react-window';
import { Dataset, useDataset } from '../../../stores/dataset';
import tw, { styled } from 'twin.macro';
import { shallow } from 'zustand/shallow';
import { RowHeightContext } from '../rowHeightContext';
import { State as StoreState, useStore } from '../store';

const RowItemWrapper = styled.div(({ isOverlay = false }: { isOverlay?: boolean }) => [
    tw`flex flex-col items-center border-b border-r border-gray-400 bg-gray-100`,
    isOverlay && tw`border-none shadow`,
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
        (event: MouseEvent<HTMLDivElement>) => {
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
    const { isDragging, ref } = useSortable({
        id: view.key,
        index,
    });

    return (
        <RowItem
            ref={ref}
            index={index}
            style={{
                ...style,
                opacity: isDragging ? 0 : 1,
            }}
        />
    );
};

type RowItemProps = HTMLAttributes<HTMLDivElement> & {
    index: number;
    style: CSSProperties;
    isOverlay?: boolean;
};

export const RowItem = forwardRef<HTMLDivElement, RowItemProps>(
    ({ index, style, isOverlay, ...props }, ref) => (
        <RowItemWrapper {...props} ref={ref} style={style} isOverlay={isOverlay}>
            <RowContent index={index} />
        </RowItemWrapper>
    )
);
RowItem.displayName = 'RowItem';

type ItemProps = {
    index: number;
};

const removeViewSelector = (state: StoreState) => state.removeLens;

const RowContent: FunctionComponent<ItemProps> = ({ index }) => {
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
            <ViewNameWrapper>
                <Tooltip content={longViewName} followCursor={true}>
                    <ViewName>{viewName}</ViewName>
                </Tooltip>
            </ViewNameWrapper>
        </>
    );
};

export default RowFactory;

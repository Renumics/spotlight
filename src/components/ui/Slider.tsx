import useResizeObserver from '@react-hook/resize-observer';
import _ from 'lodash';
import {
    createContext,
    FunctionComponent,
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import ReactSlider from 'react-slider';
import tw, { styled } from 'twin.macro';
import Popup from './Popup';

const SliderContext = createContext<{
    showTooltip: boolean;
    tooltip?: (value: number) => string;
    marks?: { [key: number]: string };
}>({
    showTooltip: false,
});

const SLIDER_HEIGHT = 14;
const SLIDER_WIDTH = 14;

const StyledSlider = styled(ReactSlider)`
    ${tw`w-full content-end flex`}
    height: ${SLIDER_HEIGHT}px;
    .mark ~ .mark {
        background: none;
        transform: translateX(calc(-50% + ${SLIDER_WIDTH / 2}px)) !important;
    }
    & .mark:last-child {
        transform: none !important;
        right: 0 !important;
        left: unset !important;
    }
` as unknown as typeof ReactSlider;

const StyledThumb = styled.div`
    cursor: grab;
    ${tw`h-full bg-white border-2 border-blue-200 border-solid hover:border-blue-300 focus-visible:outline-none box-border rounded-full`}
    height: ${SLIDER_HEIGHT}px;
    width: ${SLIDER_WIDTH}px;
    z-index: unset;
`;

const defaultTooltipFunction = (value: number) => `${value}`;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Thumb = (props: any, state: any) => {
    const { style, ...thumbProps } = props;

    return (
        <SliderContext.Consumer key={props.key}>
            {({ showTooltip, tooltip = defaultTooltipFunction }) => {
                if (showTooltip) {
                    return (
                        <Popup
                            content={
                                <span tw="text-xs align-middle font-normal text-midnight-100">
                                    {tooltip(state.value)}
                                </span>
                            }
                            delay={0}
                            followCursor={true}
                        >
                            <StyledThumb {...thumbProps} style={style} />
                        </Popup>
                    );
                }
                return <StyledThumb {...thumbProps} style={style} />;
            }}
        </SliderContext.Consumer>
    );
};

const StyledTrack = styled.div<{ active: boolean }>(({ active }) => [
    tw`h-1 bg-gray-200 place-self-center rounded-full`,
    `height: 4px`,
    active && tw`bg-blue-200`,
]);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Track = (props: any, state: any) => {
    return <StyledTrack {...props} index={state.index} active={state.index === 0} />;
};

const StyledMark = styled.div`
    ${tw`text-xs`}
    top: ${SLIDER_HEIGHT}px;
`;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Mark = (props: any) => {
    return (
        <SliderContext.Consumer key={props.key}>
            {({ marks }) => <StyledMark {...props}>{marks?.[props.key]}</StyledMark>}
        </SliderContext.Consumer>
    );
};

interface Props {
    min?: number;
    max?: number;
    marks?: { [key: number]: string };
    value?: number;
    step?: number;
    showTooltip?: boolean;
    tooltip?: (value: number) => string;
    onChange?: (value: number) => void;
    onRelease?: (value: number) => void;
    disabled?: boolean;
}

const Slider: FunctionComponent<Props> = ({
    min,
    max,
    marks,
    value = 0,
    step = 1,
    showTooltip = false,
    tooltip,
    onChange,
    onRelease,
    disabled,
}) => {
    const [valueState, setValueState] = useState(value);
    const ref = useRef<HTMLDivElement>(null);
    const sliderRef = useRef<ReactSlider>(null);
    useResizeObserver(ref.current, () => sliderRef.current?.resize());

    useEffect(() => {
        setValueState(value);
    }, [value]);

    const handleOnChange = useCallback(
        (val: number) => {
            setValueState(val);
            onChange?.(val);
        },
        [onChange]
    );

    const [minPos, maxPos] = useMemo(() => {
        const positions = marks ? Object.keys(marks).map((key) => parseFloat(key)) : [];
        return [_.min(positions), _.max(positions)];
    }, [marks]);

    const sliderMin = min ?? minPos;
    const sliderMax = max ?? maxPos;

    const markTicks = useMemo(
        () => marks && Object.keys(marks).map((key) => parseFloat(key)),
        [marks]
    );

    return (
        <div
            tw="w-full"
            style={{ height: markTicks ? SLIDER_HEIGHT + 16 : SLIDER_HEIGHT }}
            ref={ref}
        >
            <SliderContext.Provider value={{ showTooltip, tooltip, marks }}>
                <StyledSlider
                    ref={sliderRef}
                    min={sliderMin}
                    max={sliderMax}
                    value={valueState}
                    marks={markTicks}
                    step={step}
                    renderMark={marks && Mark}
                    renderTrack={Track}
                    renderThumb={Thumb}
                    onChange={handleOnChange}
                    onAfterChange={onRelease}
                    disabled={disabled}
                />
            </SliderContext.Provider>
        </div>
    );
};

export default Slider;

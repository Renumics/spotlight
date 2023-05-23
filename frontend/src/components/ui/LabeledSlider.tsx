import * as React from 'react';
import tw from 'twin.macro';
import Slider from './Slider';

const Wrapper = tw.div`flex`;
const LabeledSlider: React.FunctionComponent<
    React.ComponentProps<typeof Slider> & { className?: string }
> = (props) => {
    const { className, ...sliderProps } = props;
    const { value, min, max } = sliderProps;
    return (
        <Wrapper className={className}>
            <div tw="flex flex-col items-center w-full">
                <span>{value}</span>
                <Slider {...sliderProps} />
                <div tw="flex w-full justify-between">
                    <span>{min}</span>
                    <span>{max}</span>
                </div>
            </div>
        </Wrapper>
    );
};

export default LabeledSlider;

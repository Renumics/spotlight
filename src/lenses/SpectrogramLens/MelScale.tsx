import * as d3 from 'd3';

interface MelScale {
    (value: number): number;
    toMelScale(value: number): number;
    fromMelScale(frequency: number): number;
    domain(): number[];
    domain(domain: number[]): MelScale;
    range(): number[];
    range(range: number[]): MelScale;
    copy(): MelScale;
    invert(value: number): number;
    ticks(count?: number): number[];
    tickFormat(count?: number, specifier?: string): (d: number) => string;
}

const melScale = (): MelScale => {
    // Create the base log scale
    const linearScale = d3.scaleLinear();
    const logScale = d3.scaleLog();

    // Our custom scale function
    const scale: MelScale = ((value: number) => {
        return linearScale(value);
    }) as MelScale;

    scale.toMelScale = (frequency: number): number => {
        return 2595 * Math.log10(1 + frequency / 700);
    };

    scale.fromMelScale = (mel: number): number => {
        return 700 * (Math.pow(10, mel / 2595) - 1);
    };

    // Copy methods from the log scale
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    scale.domain = (domain?: number[]): any => {
        if (domain === undefined) {
            return linearScale.domain().map((d) => scale.toMelScale(d));
        }
        logScale.domain(domain);
        return domain ? (linearScale.domain(domain), scale) : linearScale.domain();
    };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    scale.range = (range?: number[]): any => {
        if (range) logScale.range(range);
        return range ? (linearScale.range(range), scale) : linearScale.range();
    };
    scale.copy = () => {
        return melScale().domain(scale.domain()).range(scale.range());
    };
    scale.invert = (value: number): number => {
        return scale.fromMelScale(linearScale.invert(value));
    };

    scale.ticks = (count?: number): number[] => {
        const ticks = logScale.ticks(count).map((val) => {
            return scale.toMelScale(val);
        });
        if (!count) return ticks;

        return [ticks[0]].concat(ticks.slice(ticks.length - count, ticks.length));
    };

    return scale;
};

export default melScale;

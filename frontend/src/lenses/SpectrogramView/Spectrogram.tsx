/**
 * Omit large amount of tailing zeros.
 */
const freqType = (x: number) => {
    if (x >= 1000000) return x / 1000000;
    else if (x >= 1000) return x / 1000;
    else return x;
};

/**
 * Get appropriate SI suffix for frequency.
 */
const unitType = (x: number) => {
    if (x >= 1000000) return 'MHz';
    else if (x >= 1000) return 'KHz';
    else return 'Hz';
};

/**
 * Set window to edges to start/end of track if NaN.
 * Swap window values if start > end.
 */
const fixWindow = (
    window: [number, number] | undefined,
    duration: number
): [number, number] => {
    if (!window) return [0, duration];

    // Remove any NaN values and snap to start/end
    const fixedWindow: [number, number] = [
        isNaN(window[0]) ? 0 : window[0],
        isNaN(window[1]) ? duration : window[1],
    ];
    // Swap if start time is greater than end time
    if (fixedWindow[0] > fixedWindow[1]) {
        return [fixedWindow[1], fixedWindow[0]];
    }
    return fixedWindow;
};

export { unitType, freqType, fixWindow };

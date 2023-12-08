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

const amplitudeToDb = (amplitude: number, ref: number, amin: number) => {
    const magnitude = Math.abs(amplitude);
    const power = magnitude ** 2;
    const amin_square = amin ** 2;
    const ref_square = ref ** 2;

    const log_spec =
        10 * Math.log10(Math.max(amin_square, power)) -
        10 * Math.log10(Math.max(amin_square, ref_square));

    return log_spec;
};

const hzToMel = (freq: number) => {
    // Fill in the linear part
    const f_min = 0.0;
    const f_sp = 200.0 / 3;

    let mel = (freq - f_min) / f_sp;

    // Fill in the log-scale part
    const min_log_hz = 1000.0; // beginning of log region (Hz)
    const min_log_mel = (min_log_hz - f_min) / f_sp; // same (Mels)
    const logstep = Math.log(6.4) / 27.0; // step size for log region

    if (freq >= min_log_hz) {
        mel = min_log_mel + Math.log(freq / min_log_hz) / logstep;
    }

    return mel;
};

const melToHz = (mel: number) => {
    const f_min = 0.0;
    const f_sp = 200.0 / 3;
    let freq = f_min + f_sp * mel;

    // And now the nonlinear scale
    const min_log_hz = 1000.0; // beginning of log region (Hz)
    const min_log_mel = (min_log_hz - f_min) / f_sp; // same (Mels)
    const logstep = Math.log(6.4) / 27.0; // step size for log region

    if (mel >= min_log_mel) {
        // If we have scalar data, check directly
        freq = min_log_hz * Math.exp(logstep * (mel - min_log_mel));
    }
    return freq;
};

export { unitType, freqType, fixWindow, amplitudeToDb, hzToMel, melToHz };

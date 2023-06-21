import * as Comlink from 'comlink';

const FFTWorker = {
    //bufferSize: number;
    //reverseTable: Uint32Array;
    //windowValues: Float32Array;
    //sinTable: Float32Array;
    //cosTable: Float32Array;
    initTables(
        bufferSize: number,
        sampleRate: number,
        windowFunc: string,
        alpha: number
    ) {
        const sinTable = new Float32Array(bufferSize);
        const cosTable = new Float32Array(bufferSize);
        const windowValues = new Float32Array(bufferSize);
        const reverseTable = new Uint32Array(bufferSize);
        let i;
        switch (windowFunc) {
            case 'bartlett':
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] =
                        (2 / (bufferSize - 1)) *
                        ((bufferSize - 1) / 2 - Math.abs(i - (bufferSize - 1) / 2));
                }
                break;
            case 'bartlettHann':
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] =
                        0.62 -
                        0.48 * Math.abs(i / (bufferSize - 1) - 0.5) -
                        0.38 * Math.cos((Math.PI * 2 * i) / (bufferSize - 1));
                }
                break;
            case 'blackman':
                alpha = alpha || 0.16;
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] =
                        (1 - alpha) / 2 -
                        0.5 * Math.cos((Math.PI * 2 * i) / (bufferSize - 1)) +
                        (alpha / 2) * Math.cos((4 * Math.PI * i) / (bufferSize - 1));
                }
                break;
            case 'cosine':
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] = Math.cos(
                        (Math.PI * i) / (bufferSize - 1) - Math.PI / 2
                    );
                }
                break;
            case 'gauss':
                alpha = alpha || 0.25;
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] = Math.pow(
                        Math.E,
                        -0.5 *
                            Math.pow(
                                (i - (bufferSize - 1) / 2) /
                                    ((alpha * (bufferSize - 1)) / 2),
                                2
                            )
                    );
                }
                break;
            case 'hamming':
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] =
                        0.54 - 0.46 * Math.cos((Math.PI * 2 * i) / (bufferSize - 1));
                }
                break;
            case 'hann':
            case void 0:
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] =
                        0.5 * (1 - Math.cos((Math.PI * 2 * i) / (bufferSize - 1)));
                }
                break;
            case 'lanczoz':
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] =
                        Math.sin(Math.PI * ((2 * i) / (bufferSize - 1) - 1)) /
                        (Math.PI * ((2 * i) / (bufferSize - 1) - 1));
                }
                break;
            case 'rectangular':
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] = 1;
                }
                break;
            case 'triangular':
                for (i = 0; i < bufferSize; i++) {
                    windowValues[i] =
                        (2 / bufferSize) *
                        (bufferSize / 2 - Math.abs(i - (bufferSize - 1) / 2));
                }
                break;
            default:
                throw Error("No such window function '" + windowFunc + "'");
        }
        let limit = 1;
        let bit = bufferSize >> 1;
        while (limit < bufferSize) {
            for (i = 0; i < limit; i++) {
                reverseTable[i + limit] = reverseTable[i] + bit;
            }
            limit = limit << 1;
            bit = bit >> 1;
        }
        for (i = 0; i < bufferSize; i++) {
            sinTable[i] = Math.sin(-Math.PI / i);
            cosTable[i] = Math.cos(-Math.PI / i);
        }
        //const sinTable = new Float32Array(bufferSize);
        //const cosTable = new Float32Array(bufferSize);
        //const windowValues = new Float32Array(bufferSize);
        //const reverseTable = new Uint32Array(bufferSize);
        return {
            sinTable,
            cosTable,
            windowValues,
            reverseTable,
        };
    },

    calculateSpectrum(
        buffer: any,
        bufferSize: number,
        reverseTable: Uint32Array,
        windowValues: Float32Array,
        sinTable: Float32Array,
        cosTable: Float32Array
    ) {
        const real = new Float32Array(bufferSize);
        const imag = new Float32Array(bufferSize);
        const bSi = 2 / bufferSize;
        const sqrt = Math.sqrt;
        const spectrum = new Float32Array(bufferSize / 2);
        let rval;
        let ival;
        let mag;
        let peakBand = 0;
        let peak = 0;
        const k = Math.floor(Math.log(bufferSize) / Math.LN2);
        if (Math.pow(2, k) !== bufferSize) {
            throw new Error('Invalid buffer size, must be a power of 2.');
        }
        if (bufferSize !== buffer.length) {
            throw new Error(
                'Supplied buffer is not the same size as defined FFT. FFT Size: ' +
                    bufferSize +
                    ' Buffer Size: ' +
                    buffer.length
            );
        }
        let halfSize = 1,
            phaseShiftStepReal,
            phaseShiftStepImag,
            currentPhaseShiftReal,
            currentPhaseShiftImag,
            off,
            tr,
            ti,
            tmpReal;
        for (let i = 0; i < bufferSize; i++) {
            real[i] = buffer[reverseTable[i]] * windowValues[reverseTable[i]];
            imag[i] = 0;
        }
        while (halfSize < bufferSize) {
            phaseShiftStepReal = cosTable[halfSize];
            phaseShiftStepImag = sinTable[halfSize];
            currentPhaseShiftReal = 1;
            currentPhaseShiftImag = 0;
            for (let fftStep = 0; fftStep < halfSize; fftStep++) {
                let i = fftStep;
                while (i < bufferSize) {
                    off = i + halfSize;
                    tr =
                        currentPhaseShiftReal * real[off] -
                        currentPhaseShiftImag * imag[off];
                    ti =
                        currentPhaseShiftReal * imag[off] +
                        currentPhaseShiftImag * real[off];
                    real[off] = real[i] - tr;
                    imag[off] = imag[i] - ti;
                    real[i] += tr;
                    imag[i] += ti;
                    i += halfSize << 1;
                }
                tmpReal = currentPhaseShiftReal;
                currentPhaseShiftReal =
                    tmpReal * phaseShiftStepReal -
                    currentPhaseShiftImag * phaseShiftStepImag;
                currentPhaseShiftImag =
                    tmpReal * phaseShiftStepImag +
                    currentPhaseShiftImag * phaseShiftStepReal;
            }
            halfSize = halfSize << 1;
        }
        for (let i = 0, N = bufferSize / 2; i < N; i++) {
            rval = real[i];
            ival = imag[i];
            mag = bSi * sqrt(rval * rval + ival * ival);
            if (mag > peak) {
                peakBand = i;
                peak = mag;
            }
            spectrum[i] = mag;
        }
        return spectrum;
    },

    testFunc() {
        console.log('whooooop');
    },

    calculateFrequencies(
        bufferSize: number,
        sampleRate: number,
        windowFunc: string,
        alpha: number,
        e: any
    ) {
        //throw JSON.stringify({data:'whooooop'});
        console.log('whooop');
        const data = e.data;
        const width = data.width;
        const fftSamples = data.fftSamples;
        const frequencies = [];
        const uniqueSamplesPerPx = data.channelData.length / width;
        const noverlap = Math.min(
            fftSamples - 1,
            Math.round(Math.max(0, fftSamples - uniqueSamplesPerPx))
        );
        const prep = this.initTables(bufferSize, sampleRate, windowFunc, alpha);
        const channels = 1;
        for (let c = 0; c < channels; c++) {
            const channelData = data.channelData;
            const channelFreq = [];
            let currentOffset = 0;
            while (currentOffset + fftSamples < data.channelData.length) {
                const segment = channelData.slice(
                    currentOffset,
                    currentOffset + fftSamples
                );
                const spectrum = this.calculateSpectrum(
                    segment,
                    bufferSize,
                    prep.reverseTable,
                    prep.windowValues,
                    prep.sinTable,
                    prep.cosTable
                );
                //calculateSpectrum(buffer: any,
                //bufferSize: number,
                //reverseTable: Uint32Array,
                //windowValues: Float32Array,
                //sinTable: Float32Array,
                //cosTable: Float32Array
                const array = new Uint8Array(fftSamples / 2);
                let j;
                for (j = 0; j < fftSamples / 2; j++) {
                    array[j] = Math.max(-255, Math.log10(spectrum[j]) * 45);
                }
                channelFreq.push(array);
                currentOffset += fftSamples - noverlap;
            }
            frequencies.push(channelFreq);
        }
        return frequencies[0];
    },
};

Comlink.expose(FFTWorker);

//export { FFTWorker };

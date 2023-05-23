function FFT(bufferSize, sampleRate, windowFunc, alpha) {
    this.bufferSize = bufferSize;
    this.sampleRate = sampleRate;
    this.bandwidth = (2 / bufferSize) * (sampleRate / 2);

    this.sinTable = new Float32Array(bufferSize);
    this.cosTable = new Float32Array(bufferSize);
    this.windowValues = new Float32Array(bufferSize);
    this.reverseTable = new Uint32Array(bufferSize);

    this.peakBand = 0;
    this.peak = 0;

    let i;
    switch (windowFunc) {
        case 'bartlett':
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] =
                    (2 / (bufferSize - 1)) *
                    ((bufferSize - 1) / 2 - Math.abs(i - (bufferSize - 1) / 2));
            }
            break;
        case 'bartlettHann':
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] =
                    0.62 -
                    0.48 * Math.abs(i / (bufferSize - 1) - 0.5) -
                    0.38 * Math.cos((Math.PI * 2 * i) / (bufferSize - 1));
            }
            break;
        case 'blackman':
            alpha = alpha || 0.16;
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] =
                    (1 - alpha) / 2 -
                    0.5 * Math.cos((Math.PI * 2 * i) / (bufferSize - 1)) +
                    (alpha / 2) * Math.cos((4 * Math.PI * i) / (bufferSize - 1));
            }
            break;
        case 'cosine':
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] = Math.cos(
                    (Math.PI * i) / (bufferSize - 1) - Math.PI / 2
                );
            }
            break;
        case 'gauss':
            alpha = alpha || 0.25;
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] = Math.pow(
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
                this.windowValues[i] =
                    0.54 - 0.46 * Math.cos((Math.PI * 2 * i) / (bufferSize - 1));
            }
            break;
        case 'hann':
        case undefined:
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] =
                    0.5 * (1 - Math.cos((Math.PI * 2 * i) / (bufferSize - 1)));
            }
            break;
        case 'lanczoz':
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] =
                    Math.sin(Math.PI * ((2 * i) / (bufferSize - 1) - 1)) /
                    (Math.PI * ((2 * i) / (bufferSize - 1) - 1));
            }
            break;
        case 'rectangular':
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] = 1;
            }
            break;
        case 'triangular':
            for (i = 0; i < bufferSize; i++) {
                this.windowValues[i] =
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
            this.reverseTable[i + limit] = this.reverseTable[i] + bit;
        }

        limit = limit << 1;
        bit = bit >> 1;
    }

    for (i = 0; i < bufferSize; i++) {
        this.sinTable[i] = Math.sin(-Math.PI / i);
        this.cosTable[i] = Math.cos(-Math.PI / i);
    }

    this.calculateSpectrum = function (buffer) {
        // Locally scope variables for speed up
        let bufferSize = this.bufferSize,
            cosTable = this.cosTable,
            sinTable = this.sinTable,
            reverseTable = this.reverseTable,
            real = new Float32Array(bufferSize),
            imag = new Float32Array(bufferSize),
            bSi = 2 / this.bufferSize,
            sqrt = Math.sqrt,
            rval,
            ival,
            mag,
            spectrum = new Float32Array(bufferSize / 2);

        let k = Math.floor(Math.log(bufferSize) / Math.LN2);

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
            real[i] = buffer[reverseTable[i]] * this.windowValues[reverseTable[i]];
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

            if (mag > this.peak) {
                this.peakBand = i;
                this.peak = mag;
            }
            spectrum[i] = mag;
        }
        return spectrum;
    };
}

onmessage = function (e) {
    const data = e.data;

    const width = data.width;
    const fftSamples = data.fftSamples;

    const frequencies = [];

    const uniqueSamplesPerPx = data.channelData.length / width;
    //console.log('width: ', width, ', lenght: ', data.channelData.length);

    const noverlap = Math.min(
        fftSamples - 1,
        Math.round(Math.max(0, fftSamples - uniqueSamplesPerPx))
    );

    const fft = new FFT(data.fftSamples, data.sampleRate, data.windowFunc, data.alpha);
    const channels = 1;
    //console.log(noverlap);

    for (let c = 0; c < channels; c++) {
        // for each channel TODO
        const channelData = data.channelData;
        const channelFreq = [];
        let currentOffset = 0;

        while (currentOffset + fftSamples < data.channelData.length) {
            const segment = channelData.slice(
                currentOffset,
                currentOffset + fftSamples
            );

            const spectrum = fft.calculateSpectrum(segment);

            const array = new Uint8Array(fftSamples / 2);
            let j;
            for (j = 0; j < fftSamples / 2; j++) {
                array[j] = Math.max(-255, Math.log10(spectrum[j]) * 45);
            }
            channelFreq.push(array);
            // channelFreq: [sample, freq]

            currentOffset += fftSamples - noverlap;
        }
        frequencies.push(channelFreq);
        // frequencies: [channel, sample, freq]
    }

    postMessage(frequencies[0]);
};

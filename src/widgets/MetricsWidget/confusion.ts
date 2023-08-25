interface Confusion {
    truePositives: number;
    falsePositives: number;
    trueNegatives: number;
    falseNegatives: number;
}

export function computeConfusion(actualValues: boolean[], assignedValues: boolean[]) {
    const confusion: Confusion = {
        truePositives: 0,
        falsePositives: 0,
        trueNegatives: 0,
        falseNegatives: 0,
    };

    for (let i = 0; i < actualValues.length; i++) {
        const actualValue = actualValues[i];
        const assignedValue = assignedValues[i];
        if (assignedValue) {
            if (actualValue) {
                confusion.truePositives++;
            } else {
                confusion.falsePositives++;
            }
        } else if (actualValue) {
            confusion.falseNegatives++;
        } else {
            confusion.trueNegatives++;
        }
    }

    return confusion;
}

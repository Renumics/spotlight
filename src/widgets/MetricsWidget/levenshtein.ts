export function computeLevenshtein(actualValues: boolean[], assignedValues: boolean[]): number {
    if (actualValues.length === 0) {
        return assignedValues.length;
    }
    if (assignedValues.length === 0) {
        return actualValues.length;
    }
    
    const cost = assignedValues[0] === actualValues[0] ? 0 : 1;
    
    const deletion = computeLevenshtein(actualValues.slice(1), assignedValues) + 1;
    const insertion = computeLevenshtein(actualValues, assignedValues.slice(1)) + 1;
    const substitution = computeLevenshtein(actualValues.slice(1), assignedValues.slice(1)) + cost;
    
    return Math.min(deletion, insertion, substitution);
}
export const morphStyles = ['loop', 'oscillate'] as const;
export type MorphStyle = typeof morphStyles[number];

export function calculateMorphPosition(at: number, style: MorphStyle): number {
    /*
     * This function takes a time in seconds and outputs the current "position" of the morph between -1 and 1
     * depending on the given morph style
     * - loops between 0 and 1 resets the animation when it reaches the end
     * - oscillate moves back and forth between -1 and 1
     */

    switch (style) {
        case 'oscillate':
            return Math.sin(2 * Math.PI * at);
        case 'loop':
            return at % 1;
    }
}

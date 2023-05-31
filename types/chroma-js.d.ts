// chroma-js.d.ts
import chroma from 'chroma-js';

declare module 'chroma-js' {
    interface Scale<OutType = Color> {
        nodata: (color: string | number | chroma.Color) => Scale<OutType>;
    }
}

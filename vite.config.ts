import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import dts from 'vite-plugin-dts';
import { nodePolyfills } from 'vite-plugin-node-polyfills';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    return {
        base: './',
        esbuild: {
            // https://github.com/vitejs/vite/issues/8644#issuecomment-1159308803
            logOverride: { 'this-is-undefined-in-esm': 'silent' },
        },
        plugins: [
            react({
                babel: {
                    plugins: ['babel-plugin-macros', 'babel-plugin-styled-components'],
                    compact: false,
                },
            }),
            nodePolyfills(),
            dts({
                insertTypesEntry: true,
                copyDtsFiles: true,
            }),
        ],
        build: {
            minify: true,
            outDir: './build/frontend/',
            emptyOutDir: true,
            manifest: true,
            lib: {
                entry: {
                    main: 'src/main.tsx',
                    index: 'src/lib.ts',
                    'icons/index': 'src/icons',
                },
            },
            rollupOptions: {
                output: {
                    name: 'Spotlight',
                },
            },
        },
        define: {
            'process.env.NODE_ENV': JSON.stringify(mode),
            'process.versions': '{node: "v19.4.0"}',
        },
    };
});

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    return {
        base: './',
        server: {
            watch: {
                ignored: ['**/.venv/**', '**/build/**', '**/dist/**'],
            },
        },
        plugins: [
            react(),
            babel({
                plugins: ['babel-plugin-macros', 'babel-plugin-styled-components'],
                compact: false,
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
                // In library mode Vite names the bundled CSS after the package
                // ("spotlight.css"), but the served template links "style.css".
                // Pin the name so the built stylesheet (cropper.css, tippy.css,
                // react-toastify.css, ...) is actually loaded in production.
                cssFileName: 'style',
                formats: ['es'],
            },
            rolldownOptions: {
                input: ['src/main.tsx', 'src/lib.ts'],
                output: {
                    name: 'Spotlight',
                },
            },
        },
        define: {
            'process.env.NODE_ENV': JSON.stringify(mode),
            'process.versions': '{"node": "v19.4.0"}',
        },
    };
});

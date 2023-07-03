// vite.config.ts
import { defineConfig } from "file:///home/dominik/dev/spotlight/node_modules/.pnpm/vite@4.1.0_@types+node@18.14.1/node_modules/vite/dist/node/index.js";
import react from "file:///home/dominik/dev/spotlight/node_modules/.pnpm/@vitejs+plugin-react@3.0.0_vite@4.1.0/node_modules/@vitejs/plugin-react/dist/index.mjs";
import dts from "file:///home/dominik/dev/spotlight/node_modules/.pnpm/vite-plugin-dts@2.3.0_@types+node@18.14.1_vite@4.1.0/node_modules/vite-plugin-dts/dist/index.mjs";
var vite_config_default = defineConfig(({ mode }) => {
  return {
    base: "./",
    esbuild: {
      // https://github.com/vitejs/vite/issues/8644#issuecomment-1159308803
      logOverride: { "this-is-undefined-in-esm": "silent" }
    },
    plugins: [
      react({
        babel: {
          plugins: ["babel-plugin-macros", "babel-plugin-styled-components"],
          compact: false
        }
      }),
      dts({
        insertTypesEntry: true,
        copyDtsFiles: true
      })
    ],
    build: {
      minify: true,
      outDir: "./build/frontend/",
      emptyOutDir: true,
      manifest: true,
      lib: {
        entry: {
          main: "src/main.tsx",
          index: "src/lib.ts",
          "icons/index": "src/icons"
        }
      },
      rollupOptions: {
        output: {
          name: "Spotlight"
        }
      }
    },
    define: {
      "process.env.NODE_ENV": JSON.stringify(mode)
    }
  };
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvaG9tZS9kb21pbmlrL2Rldi9zcG90bGlnaHRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIi9ob21lL2RvbWluaWsvZGV2L3Nwb3RsaWdodC92aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vaG9tZS9kb21pbmlrL2Rldi9zcG90bGlnaHQvdml0ZS5jb25maWcudHNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJztcbmltcG9ydCByZWFjdCBmcm9tICdAdml0ZWpzL3BsdWdpbi1yZWFjdCc7XG5pbXBvcnQgZHRzIGZyb20gJ3ZpdGUtcGx1Z2luLWR0cyc7XG5cbi8vIGh0dHBzOi8vdml0ZWpzLmRldi9jb25maWcvXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoKHsgbW9kZSB9KSA9PiB7XG4gICAgcmV0dXJuIHtcbiAgICAgICAgYmFzZTogJy4vJyxcbiAgICAgICAgZXNidWlsZDoge1xuICAgICAgICAgICAgLy8gaHR0cHM6Ly9naXRodWIuY29tL3ZpdGVqcy92aXRlL2lzc3Vlcy84NjQ0I2lzc3VlY29tbWVudC0xMTU5MzA4ODAzXG4gICAgICAgICAgICBsb2dPdmVycmlkZTogeyAndGhpcy1pcy11bmRlZmluZWQtaW4tZXNtJzogJ3NpbGVudCcgfSxcbiAgICAgICAgfSxcbiAgICAgICAgcGx1Z2luczogW1xuICAgICAgICAgICAgcmVhY3Qoe1xuICAgICAgICAgICAgICAgIGJhYmVsOiB7XG4gICAgICAgICAgICAgICAgICAgIHBsdWdpbnM6IFsnYmFiZWwtcGx1Z2luLW1hY3JvcycsICdiYWJlbC1wbHVnaW4tc3R5bGVkLWNvbXBvbmVudHMnXSxcbiAgICAgICAgICAgICAgICAgICAgY29tcGFjdDogZmFsc2UsXG4gICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIH0pLFxuICAgICAgICAgICAgZHRzKHtcbiAgICAgICAgICAgICAgICBpbnNlcnRUeXBlc0VudHJ5OiB0cnVlLFxuICAgICAgICAgICAgICAgIGNvcHlEdHNGaWxlczogdHJ1ZSxcbiAgICAgICAgICAgIH0pLFxuICAgICAgICBdLFxuICAgICAgICBidWlsZDoge1xuICAgICAgICAgICAgbWluaWZ5OiB0cnVlLFxuICAgICAgICAgICAgb3V0RGlyOiAnLi9idWlsZC9mcm9udGVuZC8nLFxuICAgICAgICAgICAgZW1wdHlPdXREaXI6IHRydWUsXG4gICAgICAgICAgICBtYW5pZmVzdDogdHJ1ZSxcbiAgICAgICAgICAgIGxpYjoge1xuICAgICAgICAgICAgICAgIGVudHJ5OiB7XG4gICAgICAgICAgICAgICAgICAgIG1haW46ICdzcmMvbWFpbi50c3gnLFxuICAgICAgICAgICAgICAgICAgICBpbmRleDogJ3NyYy9saWIudHMnLFxuICAgICAgICAgICAgICAgICAgICAnaWNvbnMvaW5kZXgnOiAnc3JjL2ljb25zJyxcbiAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHJvbGx1cE9wdGlvbnM6IHtcbiAgICAgICAgICAgICAgICBvdXRwdXQ6IHtcbiAgICAgICAgICAgICAgICAgICAgbmFtZTogJ1Nwb3RsaWdodCcsXG4gICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIH0sXG4gICAgICAgIH0sXG4gICAgICAgIGRlZmluZToge1xuICAgICAgICAgICAgJ3Byb2Nlc3MuZW52Lk5PREVfRU5WJzogSlNPTi5zdHJpbmdpZnkobW9kZSksXG4gICAgICAgIH0sXG4gICAgfTtcbn0pO1xuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUFtUSxTQUFTLG9CQUFvQjtBQUNoUyxPQUFPLFdBQVc7QUFDbEIsT0FBTyxTQUFTO0FBR2hCLElBQU8sc0JBQVEsYUFBYSxDQUFDLEVBQUUsS0FBSyxNQUFNO0FBQ3RDLFNBQU87QUFBQSxJQUNILE1BQU07QUFBQSxJQUNOLFNBQVM7QUFBQTtBQUFBLE1BRUwsYUFBYSxFQUFFLDRCQUE0QixTQUFTO0FBQUEsSUFDeEQ7QUFBQSxJQUNBLFNBQVM7QUFBQSxNQUNMLE1BQU07QUFBQSxRQUNGLE9BQU87QUFBQSxVQUNILFNBQVMsQ0FBQyx1QkFBdUIsZ0NBQWdDO0FBQUEsVUFDakUsU0FBUztBQUFBLFFBQ2I7QUFBQSxNQUNKLENBQUM7QUFBQSxNQUNELElBQUk7QUFBQSxRQUNBLGtCQUFrQjtBQUFBLFFBQ2xCLGNBQWM7QUFBQSxNQUNsQixDQUFDO0FBQUEsSUFDTDtBQUFBLElBQ0EsT0FBTztBQUFBLE1BQ0gsUUFBUTtBQUFBLE1BQ1IsUUFBUTtBQUFBLE1BQ1IsYUFBYTtBQUFBLE1BQ2IsVUFBVTtBQUFBLE1BQ1YsS0FBSztBQUFBLFFBQ0QsT0FBTztBQUFBLFVBQ0gsTUFBTTtBQUFBLFVBQ04sT0FBTztBQUFBLFVBQ1AsZUFBZTtBQUFBLFFBQ25CO0FBQUEsTUFDSjtBQUFBLE1BQ0EsZUFBZTtBQUFBLFFBQ1gsUUFBUTtBQUFBLFVBQ0osTUFBTTtBQUFBLFFBQ1Y7QUFBQSxNQUNKO0FBQUEsSUFDSjtBQUFBLElBQ0EsUUFBUTtBQUFBLE1BQ0osd0JBQXdCLEtBQUssVUFBVSxJQUFJO0FBQUEsSUFDL0M7QUFBQSxFQUNKO0FBQ0osQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K

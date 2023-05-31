/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_PUBLIC_URL: string;
    readonly VITE_PREVIEW_USER: string;
    readonly VITE_DOCS_URL: string;
    readonly VITE_VERSION: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}

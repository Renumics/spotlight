// a collection of compile time constants
// basically wrapping all our compile time settings
// set through import.meta.env in a typesafe interface

interface Edition {
    name: string;
    shorthand: string;
}

interface Application {
    edition: Edition;
    version: string;
    apiUrl?: string;
    publicUrl?: string;
    docsUrl: string;
    repositoryUrl: string;
    filebrowsingAllowed: boolean;
}

const application: Application = {
    edition: {
        name: 'Community',
        shorthand: 'CE',
    },
    version: import.meta.env.VITE_VERSION ?? 'dev',
    publicUrl: import.meta.env.VITE_PUBLIC_URL ?? globalThis.location.origin,
    apiUrl: import.meta.env.VITE_API_BASE_PATH ?? globalThis.location.origin,
    docsUrl: 'https://spotlight.renumics.com',
    repositoryUrl: 'https://github.com/renumics/spotlight',
    filebrowsingAllowed: window.__filebrowsing_allowed__,
} as const;

export default application;

import { create } from 'zustand';

export interface State {
    persistentErrors: string[];
    addPersistentError: (message: string) => void;
    removePersistentError: (message: string) => void;
    persistentWarnings: string[];
    addPersistentWarning: (message: string) => void;
    removePersistentWarning: (message: string) => void;
}

export const useMessages = create<State>((set) => ({
    persistentErrors: [],
    addPersistentError: (message: string) =>
        set((state) => ({ persistentErrors: [...state.persistentErrors, message] })),
    removePersistentError: (message: string) =>
        set((state) => ({
            persistentErrors: state.persistentErrors.filter((m) => m !== message),
        })),
    persistentWarnings: [],
    addPersistentWarning: (message: string) =>
        set((state) => ({
            persistentWarnings: [...state.persistentWarnings, message],
        })),
    removePersistentWarning: (message: string) =>
        set((state) => ({
            persistentWarnings: state.persistentWarnings.filter((m) => m !== message),
        })),
}));

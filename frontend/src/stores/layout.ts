import { create } from 'zustand';
import { AppLayout } from '../types';
import api from '../api';
import { saveAs } from 'file-saver';

export interface State {
    layout: AppLayout;
    reset: () => void;
    save: (layout: AppLayout) => void;
    load: (file: File) => void;
}

export const useLayout = create<State>((set) => ({
    layout: { children: [] },
    reset: () => {
        api.layout
            .resetLayout()
            .then((appLayout) => set({ layout: appLayout as AppLayout }));
    },
    save: (layout) => {
        const blob = new Blob([JSON.stringify(layout)], {
            type: 'application/json;charset=utf-8',
        });
        saveAs(blob, 'spotlight-layout.json');
    },
    load: (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            if (!e.target) return;
            const parsedLayout = JSON.parse(e.target.result as string);
            api.layout
                .setLayout({ setLayoutRequest: { layout: parsedLayout } })
                .then((appLayout) => set({ layout: appLayout as AppLayout }));
        };
        reader.readAsText(file);
    },
}));

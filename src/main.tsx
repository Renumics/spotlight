import React from 'react';
import { createRoot } from 'react-dom/client';
import GlobalStyles from './styles/GlobalStyles';
import App from './App';
import './globals';

document.addEventListener('contextmenu', (event) => event.preventDefault());

createRoot(document.getElementById('root') as HTMLElement).render(
    <React.StrictMode>
        <GlobalStyles />
        <App />
    </React.StrictMode>
);

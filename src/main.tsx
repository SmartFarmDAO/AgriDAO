import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';
import { registerServiceWorker, installPrompt, handleNetworkStatus } from './utils/pwa';

// Register PWA features
registerServiceWorker();
installPrompt();
handleNetworkStatus();

const root = createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

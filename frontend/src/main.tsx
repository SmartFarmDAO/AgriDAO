import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';
import ErrorBoundary from './components/ErrorBoundary';
import { LanguageProvider } from './components/LanguageProvider';

// Temporarily disable PWA features for debugging
// import { registerServiceWorker, installPrompt, handleNetworkStatus } from './utils/pwa';
// registerServiceWorker();
// installPrompt();
// handleNetworkStatus();

console.log('main.tsx loaded');

const rootElement = document.getElementById('root');
console.log('Root element:', rootElement);

if (!rootElement) {
  throw new Error('Root element not found');
}

const root = createRoot(rootElement);
console.log('Root created, rendering App...');

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <LanguageProvider>
        <App />
      </LanguageProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

console.log('App rendered');

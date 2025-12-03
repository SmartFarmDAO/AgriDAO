import { useState, useEffect } from 'react';

interface AppConfig {
  apiUrl: string;
}

export function useConfig() {
  const [config, setConfig] = useState<AppConfig>({ apiUrl: 'http://localhost:8000' });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch('/config.json');
        if (!response.ok) {
          console.warn('Config file not found, using defaults');
          // Use default config instead of throwing error
          setConfig({ apiUrl: 'http://localhost:8000' });
          setIsLoading(false);
          return;
        }
        const data = await response.json();
        setConfig({
          apiUrl: data.apiUrl || 'http://localhost:8000',
        });
      } catch (err) {
        console.warn('Error loading config, using defaults:', err);
        // Use default config instead of setting error
        setConfig({ apiUrl: 'http://localhost:8000' });
      } finally {
        setIsLoading(false);
      }
    };

    loadConfig();
  }, []);

  return { config, isLoading, error };
}

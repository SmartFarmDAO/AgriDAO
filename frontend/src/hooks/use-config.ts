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
          throw new Error('Failed to load configuration');
        }
        const data = await response.json();
        setConfig({
          apiUrl: data.apiUrl || 'http://localhost:8000',
        });
      } catch (err) {
        console.error('Error loading config:', err);
        setError(err instanceof Error ? err : new Error('Failed to load configuration'));
      } finally {
        setIsLoading(false);
      }
    };

    loadConfig();
  }, []);

  return { config, isLoading, error };
}

// API Configuration
export const API_CONFIG = {
  // Use relative path for API calls which will be proxied to the backend
  baseURL: import.meta.env.MODE === 'production' 
    ? 'https://yourapi.example.com' 
    : '/api',
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true, // Include cookies in requests if needed
};

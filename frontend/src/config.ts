// API Configuration
const config = {
  // Use relative path for nginx proxy
  baseURL: '/api',
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
};

export const API_CONFIG = config;
export default API_CONFIG;

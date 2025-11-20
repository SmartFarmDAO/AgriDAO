// API Configuration
const config = {
  // Use relative path for proxy in development
  baseURL: '/api',
  // You can add other API-related configurations here
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
};

export const API_CONFIG = config;

// Environment-based configuration
const env = import.meta.env.MODE || 'development';

// Override baseURL based on environment
if (env === 'production') {
  config.baseURL = 'https://api.agridao.example.com';
} else if (env === 'staging') {
  config.baseURL = 'https://staging.api.agridao.example.com';
}

export default API_CONFIG;

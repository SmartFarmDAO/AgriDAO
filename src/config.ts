// API Configuration
const config = {
  // Default to local development URL
  baseURL: 'http://localhost:8000',
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

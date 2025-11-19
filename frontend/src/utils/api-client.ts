import axios from 'axios';
import { useConfig } from '@/hooks/use-config';

// Create a custom hook that provides the API client with the current config
export function useApiClient() {
  const { config, isLoading, error } = useConfig();

  const apiClient = axios.create({
    baseURL: config.apiUrl,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    withCredentials: true, // Important for cookies/sessions
  });

  // Add request interceptor for auth tokens if needed
  apiClient.interceptors.request.use(
    (config) => {
      // You can add auth headers here if needed
      // const token = localStorage.getItem('token');
      // if (token) {
      //   config.headers.Authorization = `Bearer ${token}`;
      // }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Add response interceptor for error handling
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      // Handle common errors here (e.g., 401 unauthorized)
      if (error.response?.status === 401) {
        // Handle unauthorized
        console.error('Unauthorized access - please login');
        // Optionally redirect to login
        // window.location.href = '/auth';
      }
      return Promise.reject(error);
    }
  );

  return { apiClient, isLoading, error };
}

// Example API functions
export async function getAdvice(crop: string, location: string) {
  const response = await axios.get(`/api/ai/advice`, {
    params: { crop, location },
  });
  return response.data;
}

// Add more API functions as needed

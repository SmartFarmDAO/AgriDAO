import axios from 'axios';
import { API_CONFIG } from '@/config/api';

export async function requestOtp(email: string) {
  const res = await axios.post(
    `${API_CONFIG.baseURL}/auth/otp/request`,
    { email },
    { headers: API_CONFIG.headers, timeout: API_CONFIG.timeout, withCredentials: API_CONFIG.withCredentials }
  );
  return res.data as { 
    sent: boolean; 
    message: string;
    expires_in: number;
    dev_code?: string; 
  };
}

export async function verifyOtp(email: string, code: string) {
  const res = await axios.post(
    `${API_CONFIG.baseURL}/auth/otp/verify`,
    { email, code },
    { headers: API_CONFIG.headers, timeout: API_CONFIG.timeout, withCredentials: API_CONFIG.withCredentials }
  );
  return res.data as {
    access_token: string;
    token_type: string;
    user: { id: number; email: string; role: string };
  };
}

// OAuth and Magic Link functions removed - only email OTP authentication is supported

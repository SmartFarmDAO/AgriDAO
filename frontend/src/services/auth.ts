import axios from 'axios';
import { API_CONFIG } from '@/config/api';

export async function requestOtp(email: string) {
  const res = await axios.post(
    `${API_CONFIG.baseURL}/auth/otp/request`,
    { email },
    { headers: API_CONFIG.headers, timeout: API_CONFIG.timeout, withCredentials: API_CONFIG.withCredentials }
  );
  return res.data as { sent: boolean; dev_code?: string };
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

export async function requestMagicLink(email: string, channel: 'email' | 'whatsapp' = 'email') {
  const res = await axios.post(
    `${API_CONFIG.baseURL}/auth/magic/request`,
    { email, channel },
    { headers: API_CONFIG.headers, timeout: API_CONFIG.timeout, withCredentials: API_CONFIG.withCredentials }
  );
  return res.data as { sent: boolean; dev_link?: string; expires_in: number };
}

export function startOAuth(provider: 'google' | 'github') {
  // Redirect the browser to backend OAuth start (proxied)
  const url = `${API_CONFIG.baseURL}/auth/oauth/${provider}/start`;
  window.location.href = url;
}

export async function verifyMagicLink(token: string) {
  const url = `${API_CONFIG.baseURL}/auth/magic/verify?token=${encodeURIComponent(token)}`;
  const res = await axios.get(url, { headers: API_CONFIG.headers, timeout: API_CONFIG.timeout, withCredentials: API_CONFIG.withCredentials });
  return res.data as {
    access_token: string;
    token_type: string;
    user: { id: number; email: string; role: string };
  };
}

import CryptoJS from 'crypto-js';

const ENCRYPTION_KEY = import.meta.env.VITE_ENCRYPTION_KEY || 'default-key-change-this';

// Data encryption utilities
export const encryptData = (data: string): string => {
  return CryptoJS.AES.encrypt(data, ENCRYPTION_KEY).toString();
};

export const decryptData = (encryptedData: string): string => {
  const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
  return bytes.toString(CryptoJS.enc.Utf8);
};

// Hash sensitive data
export const hashData = (data: string): string => {
  return CryptoJS.SHA256(data).toString();
};

// Sanitize input to prevent XSS
export const sanitizeInput = (input: string): string => {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};

// Validate and sanitize file uploads
export const validateFileUpload = (file: File): { valid: boolean; error?: string } => {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/heic'];

  if (file.size > maxSize) {
    return { valid: false, error: 'File size must be less than 5MB' };
  }

  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'Only JPEG, PNG, WebP, and HEIC images are allowed' };
  }

  return { valid: true };
};

// Rate limiting helper
export class RateLimiter {
  private attempts: Map<string, { count: number; resetTime: number }> = new Map();
  private maxAttempts: number;
  private windowMs: number;

  constructor(maxAttempts: number, windowMs: number) {
    this.maxAttempts = maxAttempts;
    this.windowMs = windowMs;
  }

  checkLimit(key: string): { allowed: boolean; remaining: number; resetTime: number } {
    const now = Date.now();
    const current = this.attempts.get(key);

    if (!current || now > current.resetTime) {
      this.attempts.set(key, { count: 1, resetTime: now + this.windowMs });
      return { allowed: true, remaining: this.maxAttempts - 1, resetTime: now + this.windowMs };
    }

    if (current.count >= this.maxAttempts) {
      return { allowed: false, remaining: 0, resetTime: current.resetTime };
    }

    current.count++;
    return { allowed: true, remaining: this.maxAttempts - current.count, resetTime: current.resetTime };
  }

  reset(key: string): void {
    this.attempts.delete(key);
  }
}

// Content Security Policy helper
export const generateCSP = (): string => {
  const policies = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https: blob:",
    "font-src 'self' data:",
    "connect-src 'self' http: https: ws: wss:",
    "frame-src 'none'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ];
  
  return policies.join('; ');
};

// Privacy compliance utilities
export class PrivacyManager {
  // GDPR compliance
  static exportUserData(userId: string): Promise<Blob> {
    // Implementation would gather all user data
    const mockData = {
      userId,
      timestamp: new Date().toISOString(),
      personalData: {},
      activityLog: [],
      preferences: {},
    };
    
    return Promise.resolve(new Blob([JSON.stringify(mockData, null, 2)], { type: 'application/json' }));
  }

  static deleteUserData(userId: string): Promise<void> {
    // Implementation would delete all user data
    console.log(`Deleting all data for user: ${userId}`);
    return Promise.resolve();
  }

  static anonymizeData(data: any): any {
    // Remove or hash PII
    const anonymized = { ...data };
    
    if (anonymized.email) {
      anonymized.email = hashData(anonymized.email);
    }
    
    if (anonymized.phone) {
      anonymized.phone = hashData(anonymized.phone);
    }
    
    if (anonymized.name) {
      anonymized.name = 'REDACTED';
    }
    
    return anonymized;
  }

  static getDataRetentionPolicy(): string {
    return `
      Data Retention Policy:
      - User account data: Retained until account deletion
      - Transaction records: Retained for 7 years (regulatory requirement)
      - Analytics data: Anonymized after 26 months
      - Support tickets: Retained for 2 years after resolution
      - Marketing preferences: Retained until opt-out
    `;
  }
}

// Session security
export class SecureSession {
  static generateSessionId(): string {
    return crypto.randomUUID();
  }

  static validateSession(sessionId: string): boolean {
    // Basic validation - in real app, check against database
    return sessionId && sessionId.length === 36;
  }

  static secureHeaders() {
    return {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
    };
  }
}
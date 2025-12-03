import { z } from "zod";

/**
 * Security utilities for input validation and sanitization
 */

// Common validation schemas
export const securitySchemas = {
  email: z.string().email().max(254),
  phone: z.string().regex(/^\+?[\d\s-()]+$/).min(10).max(20),
  text: z.string().max(1000).regex(/^[^<>]*$/), // No HTML tags
  url: z.string().url().max(2048),
  filename: z.string().max(255).regex(/^[a-zA-Z0-9._-]+$/),
  alphanumeric: z.string().regex(/^[a-zA-Z0-9]+$/),
} as const;

/**
 * Sanitize HTML content to prevent XSS
 */
export const sanitizeHtml = (input: string): string => {
  return input
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;");
};

/**
 * Validate and sanitize user input
 */
export const validateInput = <T>(schema: z.ZodSchema<T>, input: unknown): T => {
  return schema.parse(input);
};

/**
 * Rate limiting state for client-side protection
 */
class RateLimiter {
  private attempts = new Map<string, { count: number; resetTime: number }>();

  isAllowed(key: string, maxAttempts: number, windowMs: number): boolean {
    const now = Date.now();
    const record = this.attempts.get(key);

    if (!record || now > record.resetTime) {
      this.attempts.set(key, { count: 1, resetTime: now + windowMs });
      return true;
    }

    if (record.count >= maxAttempts) {
      return false;
    }

    record.count++;
    return true;
  }

  reset(key: string): void {
    this.attempts.delete(key);
  }
}

export const rateLimiter = new RateLimiter();

/**
 * Secure local storage wrapper
 */
export const secureStorage = {
  set: (key: string, value: unknown): void => {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);
    } catch (error) {
      console.error("Failed to store data securely:", error);
    }
  },

  get: <T>(key: string): T | null => {
    try {
      const item = localStorage.getItem(key);
      if (!item) return null;
      
      // For access_token, return as-is (it's a JWT string)
      if (key === 'access_token' || key === 'refresh_token') {
        return item as T;
      }
      
      // For other keys, parse as JSON
      return JSON.parse(item);
    } catch (error) {
      console.error("Failed to retrieve data securely:", error);
      return null;
    }
  },

  remove: (key: string): void => {
    localStorage.removeItem(key);
  },

  clear: (): void => {
    localStorage.clear();
  },
};
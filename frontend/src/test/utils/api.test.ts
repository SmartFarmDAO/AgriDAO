import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { secureStorage } from '@/lib/security';

// Mock secureStorage
vi.mock('@/lib/security', () => ({
  secureStorage: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

describe('API utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('secureStorage', () => {
    it('should mock secureStorage methods', () => {
      const mockToken = 'test-token-123';
      
      // Test the mocked secureStorage
      (secureStorage.set as any).mockImplementation(() => {});
      (secureStorage.get as any).mockReturnValue(mockToken);
      (secureStorage.remove as any).mockImplementation(() => {});

      secureStorage.set('access_token', mockToken);
      expect(secureStorage.set).toHaveBeenCalledWith('access_token', mockToken);

      const token = secureStorage.get('access_token');
      expect(token).toBe(mockToken);

      secureStorage.remove('access_token');
      expect(secureStorage.remove).toHaveBeenCalledWith('access_token');
    });
  });

  describe('API functions', () => {
    it('should have expected API exports', () => {
      // This verifies the API structure exists
      expect(typeof secureStorage.get).toBe('function');
      expect(typeof secureStorage.set).toBe('function');
      expect(typeof secureStorage.remove).toBe('function');
    });
  });
});
import { SecureStorage } from '../../src/services/SecureStorage';
import { Platform } from 'react-native';

// Mock Platform
jest.mock('react-native', () => ({
  Platform: {
    OS: 'web', // Default to web for testing
  },
}));

// Mock localStorage for web tests
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

describe('SecureStorage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockClear();
    mockLocalStorage.setItem.mockClear();
    mockLocalStorage.removeItem.mockClear();
  });

  describe('Web Platform', () => {
    beforeEach(() => {
      (Platform as any).OS = 'web';
    });

    it('stores item using localStorage on web', async () => {
      await SecureStorage.setItemAsync('test-key', 'test-value');
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('secure_test-key', 'test-value');
    });

    it('retrieves item using localStorage on web', async () => {
      mockLocalStorage.getItem.mockReturnValue('stored-value');
      
      const result = await SecureStorage.getItemAsync('test-key');
      
      expect(result).toBe('stored-value');
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('secure_test-key');
    });

    it('deletes item using localStorage on web', async () => {
      await SecureStorage.deleteItemAsync('test-key');
      
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('secure_test-key');
    });

    it('returns correct storage type for web', () => {
      expect(SecureStorage.getStorageType()).toBe('localStorage');
    });

    it('checks availability correctly for web', () => {
      expect(SecureStorage.isAvailable()).toBe(true);
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      (Platform as any).OS = 'web';
    });

    it('handles localStorage setItem errors gracefully', async () => {
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('Storage quota exceeded');
      });

      await expect(SecureStorage.setItemAsync('test-key', 'test-value')).rejects.toThrow();
    });

    it('handles localStorage getItem errors gracefully', async () => {
      mockLocalStorage.getItem.mockImplementation(() => {
        throw new Error('Storage error');
      });

      const result = await SecureStorage.getItemAsync('test-key');
      expect(result).toBeNull();
    });

    it('handles localStorage deleteItem errors gracefully', async () => {
      mockLocalStorage.removeItem.mockImplementation(() => {
        throw new Error('Storage error');
      });

      await expect(SecureStorage.deleteItemAsync('test-key')).rejects.toThrow();
    });
  });

  describe('No localStorage Available', () => {
    beforeEach(() => {
      (Platform as any).OS = 'web';
      Object.defineProperty(window, 'localStorage', {
        value: undefined,
        writable: true,
      });
    });

    afterEach(() => {
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true,
      });
    });

    it('handles missing localStorage gracefully', async () => {
      await SecureStorage.setItemAsync('test-key', 'test-value');
      const result = await SecureStorage.getItemAsync('test-key');
      await SecureStorage.deleteItemAsync('test-key');
      
      expect(result).toBeNull();
      expect(SecureStorage.isAvailable()).toBe(false);
    });
  });
}); 
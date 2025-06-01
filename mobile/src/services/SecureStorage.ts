/**
 * Platform-aware secure storage service
 * Uses Expo SecureStore on mobile and localStorage on web
 */

import { Platform } from 'react-native';

// Conditionally import SecureStore only on native platforms
let SecureStore: any = null;
if (Platform.OS !== 'web') {
  try {
    SecureStore = require('expo-secure-store');
  } catch (error) {
    console.warn('[SecureStorage] expo-secure-store not available:', error);
  }
}

export class SecureStorage {
  /**
   * Store a value securely
   */
  static async setItemAsync(key: string, value: string): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        // Use localStorage for web
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem(`secure_${key}`, value);
        } else {
          console.warn('[SecureStorage] localStorage not available on web');
        }
      } else {
        // Use SecureStore for mobile
        if (SecureStore) {
          await SecureStore.setItemAsync(key, value);
        } else {
          console.warn('[SecureStorage] SecureStore not available, using fallback');
          // Fallback to AsyncStorage if available
          try {
            const AsyncStorage = require('@react-native-async-storage/async-storage').default;
            await AsyncStorage.setItem(`secure_${key}`, value);
          } catch (e) {
            console.error('[SecureStorage] No storage method available');
          }
        }
      }
    } catch (error) {
      console.error('[SecureStorage] Error storing item:', error);
      throw error;
    }
  }

  /**
   * Retrieve a value securely
   */
  static async getItemAsync(key: string): Promise<string | null> {
    try {
      if (Platform.OS === 'web') {
        // Use localStorage for web
        if (typeof localStorage !== 'undefined') {
          return localStorage.getItem(`secure_${key}`);
        } else {
          console.warn('[SecureStorage] localStorage not available on web');
          return null;
        }
      } else {
        // Use SecureStore for mobile
        if (SecureStore) {
          return await SecureStore.getItemAsync(key);
        } else {
          console.warn('[SecureStorage] SecureStore not available, using fallback');
          // Fallback to AsyncStorage if available
          try {
            const AsyncStorage = require('@react-native-async-storage/async-storage').default;
            return await AsyncStorage.getItem(`secure_${key}`);
          } catch (e) {
            console.error('[SecureStorage] No storage method available');
            return null;
          }
        }
      }
    } catch (error) {
      console.error('[SecureStorage] Error retrieving item:', error);
      return null;
    }
  }

  /**
   * Remove a value securely
   */
  static async deleteItemAsync(key: string): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        // Use localStorage for web
        if (typeof localStorage !== 'undefined') {
          localStorage.removeItem(`secure_${key}`);
        } else {
          console.warn('[SecureStorage] localStorage not available on web');
        }
      } else {
        // Use SecureStore for mobile
        if (SecureStore) {
          await SecureStore.deleteItemAsync(key);
        } else {
          console.warn('[SecureStorage] SecureStore not available, using fallback');
          // Fallback to AsyncStorage if available
          try {
            const AsyncStorage = require('@react-native-async-storage/async-storage').default;
            await AsyncStorage.removeItem(`secure_${key}`);
          } catch (e) {
            console.error('[SecureStorage] No storage method available');
          }
        }
      }
    } catch (error) {
      console.error('[SecureStorage] Error deleting item:', error);
      throw error;
    }
  }

  /**
   * Check if storage is available
   */
  static isAvailable(): boolean {
    if (Platform.OS === 'web') {
      return typeof localStorage !== 'undefined';
    } else {
      return SecureStore !== null;
    }
  }

  /**
   * Get storage type being used
   */
  static getStorageType(): string {
    if (Platform.OS === 'web') {
      return 'localStorage';
    } else if (SecureStore) {
      return 'SecureStore';
    } else {
      return 'AsyncStorage';
    }
  }
}

export default SecureStorage; 
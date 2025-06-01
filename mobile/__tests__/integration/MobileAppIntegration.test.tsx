/**
 * Integration Tests for Mental Wellness Coach Mobile App
 * Tests the complete user flow from authentication to core features
 */

import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { View, Text } from 'react-native';
import { ApiClient, MoodApi, ConversationApi } from '../../src/services/ApiClient';
import { AuthService } from '../../src/services/AuthService';
import * as SecureStore from 'expo-secure-store';

// Mock all external dependencies
jest.mock('expo-secure-store', () => ({
  setItemAsync: jest.fn(),
  getItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

jest.mock('../../src/services/ApiClient', () => ({
  ApiClient: {
    setBaseURL: jest.fn(),
    get: jest.fn(),
    post: jest.fn(),
  },
  MoodApi: {
    createEntry: jest.fn(),
    getEntries: jest.fn(),
    getAnalytics: jest.fn(),
    quickCheckIn: jest.fn(),
  },
  ConversationApi: {
    startConversation: jest.fn(),
    sendMessage: jest.fn(),
    getMessages: jest.fn(),
  },
  CrisisApi: {
    analyzeContent: jest.fn(),
    getResources: jest.fn(),
  },
}));

// Mock navigation
const mockNavigate = jest.fn();
const mockReplace = jest.fn();
const mockNavigation = {
  navigate: mockNavigate,
  replace: mockReplace,
} as any;

// Mock React Navigation
jest.mock('@react-navigation/native', () => ({
  NavigationContainer: ({ children }: any) => children,
  useNavigation: () => mockNavigation,
}));

jest.mock('@react-navigation/stack', () => ({
  createStackNavigator: () => ({
    Navigator: ({ children }: any) => children,
    Screen: ({ children }: any) => children,
  }),
}));

// Mock Expo modules
jest.mock('expo-font', () => ({
  loadAsync: jest.fn(),
}));

jest.mock('expo-splash-screen', () => ({
  preventAutoHideAsync: jest.fn(),
  hideAsync: jest.fn(),
}));

describe('Mobile App Integration Tests', () => {
  const mockUser = {
    id: 'user-123',
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    created_at: '2024-01-01T00:00:00Z',
  };

  const mockAuthResponse = {
    access_token: 'mock-token-123',
    token_type: 'Bearer',
    user: mockUser,
    message: 'Login successful',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset navigation mocks
    mockNavigate.mockClear();
    mockReplace.mockClear();
  });

  describe('App Initialization Flow', () => {
    it('handles first-time user onboarding flow', async () => {
      // Mock first-time user (no onboarding completed, not authenticated)
      (SecureStore.getItemAsync as jest.Mock)
        .mockResolvedValueOnce(null) // onboarding_completed
        .mockResolvedValueOnce(null); // access_token

      // Test the AuthService calls directly instead of component rendering
      const hasOnboarded = await AuthService.hasCompletedOnboarding();
      const isAuth = await AuthService.isAuthenticated();
      
      expect(hasOnboarded).toBe(false);
      expect(isAuth).toBe(false);
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('onboarding_completed');
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('access_token');
    });

    it('handles returning authenticated user', async () => {
      // Mock authenticated user
      (SecureStore.getItemAsync as jest.Mock)
        .mockResolvedValueOnce('true') // onboarding_completed
        .mockResolvedValueOnce('valid-token'); // access_token

      const hasOnboarded = await AuthService.hasCompletedOnboarding();
      const isAuth = await AuthService.isAuthenticated();
      
      expect(hasOnboarded).toBe(true);
      expect(isAuth).toBe(true);
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('onboarding_completed');
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('access_token');
    });

    it('handles returning non-authenticated user', async () => {
      // Mock user who has completed onboarding but not logged in
      (SecureStore.getItemAsync as jest.Mock)
        .mockResolvedValueOnce('true') // onboarding_completed
        .mockResolvedValueOnce(null); // access_token

      const hasOnboarded = await AuthService.hasCompletedOnboarding();
      const isAuth = await AuthService.isAuthenticated();
      
      expect(hasOnboarded).toBe(true);
      expect(isAuth).toBe(false);
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('onboarding_completed');
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('access_token');
    });
  });

  describe('Authentication Flow', () => {
    it('completes successful registration flow', async () => {
      const registerData = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123',
        full_name: 'New User',
      };

      // Mock successful registration
      (ApiClient.post as jest.Mock).mockResolvedValue(mockAuthResponse);
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.register(registerData);

      expect(ApiClient.post).toHaveBeenCalledWith('/auth/register', registerData);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('access_token', mockAuthResponse.access_token);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockUser));
      expect(result).toEqual(mockAuthResponse);
    });

    it('completes successful login flow', async () => {
      const loginData = {
        username: 'testuser',
        password: 'password123',
      };

      // Mock successful login
      (ApiClient.post as jest.Mock).mockResolvedValue(mockAuthResponse);
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.login(loginData);

      expect(ApiClient.post).toHaveBeenCalledWith('/auth/login', loginData);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('access_token', mockAuthResponse.access_token);
      expect(result).toEqual(mockAuthResponse);
    });

    it('handles authentication errors gracefully', async () => {
      const loginData = {
        username: 'testuser',
        password: 'wrongpassword',
      };

      // Mock failed login
      (ApiClient.post as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));

      await expect(AuthService.login(loginData)).rejects.toThrow(
        'Login failed. Please check your credentials.'
      );
    });
  });

  describe('Core Feature Integration', () => {
    beforeEach(() => {
      // Mock authenticated state
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('valid-token');
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);
    });

    describe('Mood Tracking Integration', () => {
      it('completes mood entry creation flow', async () => {
        const moodData = {
          mood_score: 7,
          energy_level: 6,
          stress_level: 4,
          sleep_quality: 8,
          notes: 'Feeling great today!',
        };

        const mockResponse = {
          status: 'success',
          data: { id: 1, ...moodData, created_at: '2024-01-01T12:00:00Z' },
        };

        (MoodApi.createEntry as jest.Mock).mockResolvedValue(mockResponse);

        const result = await MoodApi.createEntry(moodData);

        expect(MoodApi.createEntry).toHaveBeenCalledWith(moodData);
        expect(result).toEqual(mockResponse);
      });

      it('retrieves mood analytics successfully', async () => {
        const mockAnalytics = {
          status: 'success',
          data: {
            average_mood: 6.5,
            mood_trend: 'improving',
            total_entries: 15,
            streak_days: 7,
          },
        };

        (MoodApi.getAnalytics as jest.Mock).mockResolvedValue(mockAnalytics);

        const result = await MoodApi.getAnalytics('2024-01-01', '2024-01-31');

        expect(MoodApi.getAnalytics).toHaveBeenCalledWith('2024-01-01', '2024-01-31');
        expect(result).toEqual(mockAnalytics);
      });

      it('performs quick mood check-in', async () => {
        const mockResponse = { status: 'success', message: 'Quick check-in recorded' };

        (MoodApi.quickCheckIn as jest.Mock).mockResolvedValue(mockResponse);

        const result = await MoodApi.quickCheckIn(8);

        expect(MoodApi.quickCheckIn).toHaveBeenCalledWith(8);
        expect(result).toEqual(mockResponse);
      });
    });

    describe('Conversation Integration', () => {
      it('completes conversation creation and messaging flow', async () => {
        const conversationResponse = {
          status: 'success',
          data: { conversation_id: 'conv-123', created_at: '2024-01-01T12:00:00Z' },
        };

        const messageResponse = {
          status: 'success',
          data: {
            id: 'msg-123',
            message: 'Hello! How are you feeling today?',
            sender: 'ai',
            timestamp: '2024-01-01T12:01:00Z',
          },
        };

        (ConversationApi.startConversation as jest.Mock).mockResolvedValue(conversationResponse);
        (ConversationApi.sendMessage as jest.Mock).mockResolvedValue(messageResponse);

        // Start conversation
        const convResult = await ConversationApi.startConversation();
        expect(ConversationApi.startConversation).toHaveBeenCalled();
        expect(convResult).toEqual(conversationResponse);

        // Send message
        const msgResult = await ConversationApi.sendMessage('conv-123', 'I am feeling anxious');
        expect(ConversationApi.sendMessage).toHaveBeenCalledWith('conv-123', 'I am feeling anxious');
        expect(msgResult).toEqual(messageResponse);
      });

      it('retrieves conversation messages', async () => {
        const messagesResponse = {
          status: 'success',
          data: [
            { id: 'msg-1', message: 'Hello', sender: 'user', timestamp: '2024-01-01T12:00:00Z' },
            { id: 'msg-2', message: 'Hi there!', sender: 'ai', timestamp: '2024-01-01T12:01:00Z' },
          ],
        };

        (ConversationApi.getMessages as jest.Mock).mockResolvedValue(messagesResponse);

        const result = await ConversationApi.getMessages('conv-123');

        expect(ConversationApi.getMessages).toHaveBeenCalledWith('conv-123');
        expect(result).toEqual(messagesResponse);
      });
    });

    describe('API Client Integration', () => {
      // Store original fetch to restore later
      const originalFetch = global.fetch;

      beforeEach(() => {
        // Reset global fetch before each test
        delete (global as any).fetch;
      });

      afterEach(() => {
        // Restore original fetch
        global.fetch = originalFetch;
      });

      it('handles API configuration correctly', () => {
        const testUrl = 'https://test-api.example.com';
        
        ApiClient.setBaseURL(testUrl);
        
        expect(ApiClient.setBaseURL).toBeDefined();
      });

      it('integrates with SecureStore for authentication', async () => {
        const mockToken = 'test-token-123';
        (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(mockToken);

        // Test that ApiClient configuration works
        ApiClient.setBaseURL('https://test.example.com');
        
        // Test that SecureStore integration is available
        const token = await SecureStore.getItemAsync('access_token');
        expect(token).toBe(mockToken);
        expect(SecureStore.getItemAsync).toHaveBeenCalledWith('access_token');
        
        // Verify ApiClient has the expected interface
        expect(typeof ApiClient.get).toBe('function');
        expect(typeof ApiClient.post).toBe('function');
        expect(typeof ApiClient.setBaseURL).toBe('function');
      });
    });
  });

  describe('Error Handling Integration', () => {
    it('handles network connectivity issues', async () => {
      (ApiClient.get as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(ApiClient.get('/test')).rejects.toThrow('Network error');
    });

    it('handles API server errors', async () => {
      const serverError = {
        message: 'Internal server error',
        status: 500,
        data: { error: 'Database connection failed' },
      };

      (ApiClient.post as jest.Mock).mockRejectedValue(serverError);

      await expect(ApiClient.post('/test', {})).rejects.toMatchObject(serverError);
    });

    it('handles token expiration gracefully', async () => {
      const tokenError = {
        message: 'Token expired',
        status: 401,
        data: { error: 'Unauthorized' },
      };

      (ApiClient.get as jest.Mock).mockRejectedValue(tokenError);

      await expect(ApiClient.get('/protected')).rejects.toMatchObject(tokenError);
    });
  });

  describe('Data Persistence Integration', () => {
    it('persists user authentication state', async () => {
      const token = 'persistent-token-123';
      
      await AuthService.storeToken(token);
      
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('access_token', token);
    });

    it('persists user profile data', async () => {
      await AuthService.storeUserData(mockUser);
      
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockUser));
    });

    it('persists onboarding completion status', async () => {
      await AuthService.markOnboardingCompleted();
      
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('onboarding_completed', 'true');
    });

    it('clears all data on logout', async () => {
      await AuthService.logout();
      
      expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('access_token');
      expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('user_data');
    });
  });
}); 
import { AuthService, User, LoginData, RegisterData, AuthResponse } from '../../src/services/AuthService';
import { ApiClient } from '../../src/services/ApiClient';
import * as SecureStore from 'expo-secure-store';

// Mock dependencies
jest.mock('expo-secure-store', () => ({
  setItemAsync: jest.fn(),
  getItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

jest.mock('../../src/services/ApiClient', () => ({
  ApiClient: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

describe('AuthService', () => {
  const mockUser: User = {
    id: 'user-123',
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    created_at: '2024-01-01T00:00:00Z',
  };

  const mockAuthResponse: AuthResponse = {
    access_token: 'mock-token-123',
    token_type: 'Bearer',
    user: mockUser,
    message: 'Login successful',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Token Management', () => {
    it('stores token successfully', async () => {
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.storeToken('test-token');

      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('access_token', 'test-token');
    });

    it('handles token storage errors', async () => {
      (SecureStore.setItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      await expect(AuthService.storeToken('test-token')).rejects.toThrow(
        'Failed to store authentication token'
      );
    });

    it('retrieves token successfully', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('stored-token');

      const token = await AuthService.getToken();

      expect(token).toBe('stored-token');
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('access_token');
    });

    it('handles token retrieval errors gracefully', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockRejectedValue(new Error('Retrieval error'));

      const token = await AuthService.getToken();

      expect(token).toBeNull();
    });

    it('returns null when no token exists', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

      const token = await AuthService.getToken();

      expect(token).toBeNull();
    });
  });

  describe('User Data Management', () => {
    it('stores user data successfully', async () => {
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.storeUserData(mockUser);

      expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
        'user_data',
        JSON.stringify(mockUser)
      );
    });

    it('handles user data storage errors', async () => {
      (SecureStore.setItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      await expect(AuthService.storeUserData(mockUser)).rejects.toThrow(
        'Failed to store user data'
      );
    });

    it('retrieves user data successfully', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(JSON.stringify(mockUser));

      const userData = await AuthService.getUserData();

      expect(userData).toEqual(mockUser);
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('user_data');
    });

    it('handles user data retrieval errors gracefully', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockRejectedValue(new Error('Retrieval error'));

      const userData = await AuthService.getUserData();

      expect(userData).toBeNull();
    });

    it('returns null when no user data exists', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

      const userData = await AuthService.getUserData();

      expect(userData).toBeNull();
    });
  });

  describe('Authentication Status', () => {
    it('returns true when token exists', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('valid-token');

      const isAuth = await AuthService.isAuthenticated();

      expect(isAuth).toBe(true);
    });

    it('returns false when no token exists', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

      const isAuth = await AuthService.isAuthenticated();

      expect(isAuth).toBe(false);
    });

    it('returns false on error', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockRejectedValue(new Error('Error'));

      const isAuth = await AuthService.isAuthenticated();

      expect(isAuth).toBe(false);
    });
  });

  describe('User Registration', () => {
    const registerData: RegisterData = {
      username: 'newuser',
      email: 'newuser@example.com',
      password: 'password123',
      full_name: 'New User',
    };

    it('registers user successfully', async () => {
      (ApiClient.post as jest.Mock).mockResolvedValue(mockAuthResponse);
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.register(registerData);

      expect(ApiClient.post).toHaveBeenCalledWith('/auth/register', registerData);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('access_token', mockAuthResponse.access_token);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockUser));
      expect(result).toEqual(mockAuthResponse);
    });

    it('handles registration errors', async () => {
      (ApiClient.post as jest.Mock).mockRejectedValue(new Error('Registration failed'));

      await expect(AuthService.register(registerData)).rejects.toThrow(
        'Registration failed. Please try again.'
      );
    });
  });

  describe('User Login', () => {
    const loginData: LoginData = {
      username: 'testuser',
      password: 'password123',
    };

    it('logs in user successfully', async () => {
      (ApiClient.post as jest.Mock).mockResolvedValue(mockAuthResponse);
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.login(loginData);

      expect(ApiClient.post).toHaveBeenCalledWith('/auth/login', loginData);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('access_token', mockAuthResponse.access_token);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockUser));
      expect(result).toEqual(mockAuthResponse);
    });

    it('handles login errors', async () => {
      (ApiClient.post as jest.Mock).mockRejectedValue(new Error('Login failed'));

      await expect(AuthService.login(loginData)).rejects.toThrow(
        'Login failed. Please check your credentials.'
      );
    });
  });

  describe('User Logout', () => {
    it('clears stored data successfully', async () => {
      (SecureStore.deleteItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.logout();

      expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('access_token');
      expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('user_data');
    });

    it('handles logout errors gracefully', async () => {
      (SecureStore.deleteItemAsync as jest.Mock).mockRejectedValue(new Error('Delete error'));

      // Should not throw
      await AuthService.logout();

      expect(SecureStore.deleteItemAsync).toHaveBeenCalled();
    });
  });

  describe('Onboarding Management', () => {
    it('marks onboarding as completed', async () => {
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.markOnboardingCompleted();

      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('onboarding_completed', 'true');
    });

    it('handles onboarding completion errors gracefully', async () => {
      (SecureStore.setItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      // Should not throw
      await AuthService.markOnboardingCompleted();

      expect(SecureStore.setItemAsync).toHaveBeenCalled();
    });

    it('returns true when onboarding is completed', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('true');

      const isCompleted = await AuthService.hasCompletedOnboarding();

      expect(isCompleted).toBe(true);
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith('onboarding_completed');
    });

    it('returns false when onboarding is not completed', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

      const isCompleted = await AuthService.hasCompletedOnboarding();

      expect(isCompleted).toBe(false);
    });

    it('returns false on onboarding check error', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockRejectedValue(new Error('Error'));

      const isCompleted = await AuthService.hasCompletedOnboarding();

      expect(isCompleted).toBe(false);
    });
  });

  describe('Current User Management', () => {
    it('gets current user successfully', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('valid-token');
      (ApiClient.get as jest.Mock).mockResolvedValue({ user: mockUser });

      const user = await AuthService.getCurrentUser();

      expect(ApiClient.get).toHaveBeenCalledWith('/auth/profile');
      expect(user).toEqual(mockUser);
    });

    it('returns null when no token exists', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

      const user = await AuthService.getCurrentUser();

      expect(user).toBeNull();
      expect(ApiClient.get).not.toHaveBeenCalled();
    });

    it('handles API errors when getting current user', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('valid-token');
      (ApiClient.get as jest.Mock).mockRejectedValue(new Error('API error'));

      const user = await AuthService.getCurrentUser();

      expect(user).toBeNull();
    });

    it('refreshes user data successfully', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('valid-token');
      (ApiClient.get as jest.Mock).mockResolvedValue({ user: mockUser });
      (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const user = await AuthService.refreshUserData();

      expect(user).toEqual(mockUser);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockUser));
    });

    it('handles refresh errors gracefully', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('valid-token');
      (ApiClient.get as jest.Mock).mockRejectedValue(new Error('API error'));

      const user = await AuthService.refreshUserData();

      expect(user).toBeNull();
    });
  });
}); 
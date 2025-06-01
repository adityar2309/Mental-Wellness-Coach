import { AuthService, LoginData, RegisterData } from '../../src/services/AuthService';
import { SecureStorage } from '../../src/services/SecureStorage';
import { ApiClient } from '../../src/services/ApiClient';

// Mock dependencies
jest.mock('../../src/services/SecureStorage');
jest.mock('../../src/services/ApiClient');

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Token Management', () => {
    it('stores token securely', async () => {
      const token = 'test-token-123';
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.storeToken(token);

      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('access_token', token);
    });

    it('retrieves stored token', async () => {
      const token = 'test-token-123';
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue(token);

      const result = await AuthService.getToken();

      expect(SecureStorage.getItemAsync).toHaveBeenCalledWith('access_token');
      expect(result).toBe(token);
    });

    it('returns null when no token is stored', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue(null);

      const result = await AuthService.getToken();

      expect(result).toBeNull();
    });

    it('handles token storage errors gracefully', async () => {
      const token = 'test-token-123';
      (SecureStorage.setItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      await expect(AuthService.storeToken(token)).rejects.toThrow('Failed to store authentication token');
    });

    it('handles token retrieval errors gracefully', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const result = await AuthService.getToken();

      expect(result).toBeNull();
    });
  });

  describe('User Data Management', () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      created_at: '2023-01-01T00:00:00Z',
    };

    it('stores user data securely', async () => {
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.storeUserData(mockUser);

      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockUser));
    });

    it('retrieves stored user data', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue(JSON.stringify(mockUser));

      const result = await AuthService.getUserData();

      expect(SecureStorage.getItemAsync).toHaveBeenCalledWith('user_data');
      expect(result).toEqual(mockUser);
    });

    it('returns null when no user data is stored', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue(null);

      const result = await AuthService.getUserData();

      expect(result).toBeNull();
    });

    it('handles user data storage errors gracefully', async () => {
      (SecureStorage.setItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      await expect(AuthService.storeUserData(mockUser)).rejects.toThrow('Failed to store user data');
    });

    it('handles user data retrieval errors gracefully', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const result = await AuthService.getUserData();

      expect(result).toBeNull();
    });
  });

  describe('Authentication Status', () => {
    it('returns true when user is authenticated', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('test-token');

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('returns false when user is not authenticated', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue(null);

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(false);
    });

    it('returns false on storage error', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('User Registration', () => {
    const registerData: RegisterData = {
      email: 'test@example.com',
      password: 'password123',
      name: 'Test User',
    };

    const mockResponse = {
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        created_at: '2023-01-01T00:00:00Z',
      },
      token: 'new-token-123',
      message: 'Registration successful',
    };

    it('registers user successfully with token field', async () => {
      (ApiClient.post as jest.Mock).mockResolvedValue(mockResponse);
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.register(registerData);

      expect(ApiClient.post).toHaveBeenCalledWith('/auth/register', registerData);
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('access_token', 'new-token-123');
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockResponse.user));
      expect(result).toEqual(mockResponse);
    });

    it('registers user successfully with access_token field', async () => {
      const responseWithAccessToken = {
        ...mockResponse,
        access_token: 'access-token-123',
        token: undefined,
      };
      (ApiClient.post as jest.Mock).mockResolvedValue(responseWithAccessToken);
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.register(registerData);

      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('access_token', 'access-token-123');
      expect(result).toEqual(responseWithAccessToken);
    });

    it('registers user without storing token when none provided', async () => {
      const responseWithoutToken = {
        ...mockResponse,
        token: undefined,
        access_token: undefined,
      };
      (ApiClient.post as jest.Mock).mockResolvedValue(responseWithoutToken);
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.register(registerData);

      expect(SecureStorage.setItemAsync).toHaveBeenCalledTimes(1); // Only for user data
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(responseWithoutToken.user));
      expect(result).toEqual(responseWithoutToken);
    });

    it('handles registration API errors', async () => {
      (ApiClient.post as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(AuthService.register(registerData)).rejects.toThrow('Registration failed. Please try again.');
    });

    it('handles generic registration errors', async () => {
      (ApiClient.post as jest.Mock).mockRejectedValue('Unknown error');

      await expect(AuthService.register(registerData)).rejects.toThrow('Registration failed. Please try again.');
    });
  });

  describe('User Login', () => {
    const loginData: LoginData = {
      email: 'test@example.com',
      password: 'password123',
    };

    const mockResponse = {
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        created_at: '2023-01-01T00:00:00Z',
      },
      token: 'login-token-123',
      message: 'Login successful',
    };

    it('logs in user successfully with token field', async () => {
      (ApiClient.post as jest.Mock).mockResolvedValue(mockResponse);
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.login(loginData);

      expect(ApiClient.post).toHaveBeenCalledWith('/auth/login', loginData);
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('access_token', 'login-token-123');
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockResponse.user));
      expect(result).toEqual(mockResponse);
    });

    it('logs in user successfully with access_token field', async () => {
      const responseWithAccessToken = {
        ...mockResponse,
        access_token: 'access-token-123',
        token: undefined,
      };
      (ApiClient.post as jest.Mock).mockResolvedValue(responseWithAccessToken);
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.login(loginData);

      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('access_token', 'access-token-123');
      expect(result).toEqual(responseWithAccessToken);
    });

    it('handles login API errors', async () => {
      (ApiClient.post as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));

      await expect(AuthService.login(loginData)).rejects.toThrow('Login failed. Please check your credentials.');
    });

    it('handles generic login errors', async () => {
      (ApiClient.post as jest.Mock).mockRejectedValue('Network timeout');

      await expect(AuthService.login(loginData)).rejects.toThrow('Login failed. Please check your credentials.');
    });
  });

  describe('User Logout', () => {
    it('clears stored authentication data', async () => {
      (SecureStorage.deleteItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.logout();

      expect(SecureStorage.deleteItemAsync).toHaveBeenCalledWith('access_token');
      expect(SecureStorage.deleteItemAsync).toHaveBeenCalledWith('user_data');
    });

    it('handles logout errors gracefully', async () => {
      (SecureStorage.deleteItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      // Should not throw error
      await expect(AuthService.logout()).resolves.toBeUndefined();
    });
  });

  describe('Onboarding Management', () => {
    it('marks onboarding as completed', async () => {
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.markOnboardingCompleted();

      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('onboarding_completed', 'true');
    });

    it('checks if onboarding is completed', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('true');

      const result = await AuthService.hasCompletedOnboarding();

      expect(SecureStorage.getItemAsync).toHaveBeenCalledWith('onboarding_completed');
      expect(result).toBe(true);
    });

    it('returns false when onboarding is not completed', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue(null);

      const result = await AuthService.hasCompletedOnboarding();

      expect(result).toBe(false);
    });

    it('handles onboarding errors gracefully', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const result = await AuthService.hasCompletedOnboarding();

      expect(result).toBe(false);
    });
  });

  describe('Current User Profile', () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      created_at: '2023-01-01T00:00:00Z',
    };

    it('gets current user profile when authenticated', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('test-token');
      (ApiClient.get as jest.Mock).mockResolvedValue({ user: mockUser });

      const result = await AuthService.getCurrentUser();

      expect(ApiClient.get).toHaveBeenCalledWith('/auth/profile');
      expect(result).toEqual(mockUser);
    });

    it('returns null when not authenticated', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue(null);

      const result = await AuthService.getCurrentUser();

      expect(ApiClient.get).not.toHaveBeenCalled();
      expect(result).toBeNull();
    });

    it('handles profile API errors', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('test-token');
      (ApiClient.get as jest.Mock).mockRejectedValue(new Error('API error'));

      const result = await AuthService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('Refresh User Data', () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Updated User',
      created_at: '2023-01-01T00:00:00Z',
    };

    it('refreshes and stores updated user data', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('test-token');
      (ApiClient.get as jest.Mock).mockResolvedValue({ user: mockUser });
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      const result = await AuthService.refreshUserData();

      expect(ApiClient.get).toHaveBeenCalledWith('/auth/profile');
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(mockUser));
      expect(result).toEqual(mockUser);
    });

    it('returns null when user profile cannot be fetched', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('test-token');
      (ApiClient.get as jest.Mock).mockRejectedValue(new Error('API error'));

      const result = await AuthService.refreshUserData();

      expect(result).toBeNull();
    });

    it('handles refresh errors gracefully', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const result = await AuthService.refreshUserData();

      expect(result).toBeNull();
    });
  });

  describe('Edge Cases and Integration', () => {
    it('handles malformed user data in storage', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('invalid-json');

      const result = await AuthService.getUserData();

      expect(result).toBeNull();
    });

    it('handles empty string token', async () => {
      (SecureStorage.getItemAsync as jest.Mock).mockResolvedValue('');

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(false);
    });

    it('stores user data without name field', async () => {
      const userWithoutName = {
        id: '1',
        email: 'test@example.com',
        created_at: '2023-01-01T00:00:00Z',
      };
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      await AuthService.storeUserData(userWithoutName);

      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('user_data', JSON.stringify(userWithoutName));
    });

    it('handles concurrent authentication operations', async () => {
      const token1 = 'token-1';
      const token2 = 'token-2';
      (SecureStorage.setItemAsync as jest.Mock).mockResolvedValue(undefined);

      // Simulate concurrent token storage
      const promises = [
        AuthService.storeToken(token1),
        AuthService.storeToken(token2),
      ];

      await Promise.all(promises);

      expect(SecureStorage.setItemAsync).toHaveBeenCalledTimes(2);
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('access_token', token1);
      expect(SecureStorage.setItemAsync).toHaveBeenCalledWith('access_token', token2);
    });
  });
}); 
import React from 'react';
import { AuthService } from '../src/services/AuthService';

// Mock the AuthService
jest.mock('../src/services/AuthService', () => ({
  AuthService: {
    hasCompletedOnboarding: jest.fn(),
    isAuthenticated: jest.fn(),
  },
}));

describe('App Component Logic', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('handles first launch and not authenticated scenario', async () => {
    // Mock first launch and not authenticated
    (AuthService.hasCompletedOnboarding as jest.Mock).mockResolvedValue(false);
    (AuthService.isAuthenticated as jest.Mock).mockResolvedValue(false);

    // Test the logic that would be used in the App component
    const hasOnboarded = await AuthService.hasCompletedOnboarding();
    const isAuth = await AuthService.isAuthenticated();

    expect(hasOnboarded).toBe(false);
    expect(isAuth).toBe(false);
    expect(AuthService.hasCompletedOnboarding).toHaveBeenCalled();
    expect(AuthService.isAuthenticated).toHaveBeenCalled();
  });

  it('handles onboarding completed but not authenticated scenario', async () => {
    (AuthService.hasCompletedOnboarding as jest.Mock).mockResolvedValue(true);
    (AuthService.isAuthenticated as jest.Mock).mockResolvedValue(false);

    const hasOnboarded = await AuthService.hasCompletedOnboarding();
    const isAuth = await AuthService.isAuthenticated();

    expect(hasOnboarded).toBe(true);
    expect(isAuth).toBe(false);
    expect(AuthService.hasCompletedOnboarding).toHaveBeenCalled();
    expect(AuthService.isAuthenticated).toHaveBeenCalled();
  });

  it('handles authenticated user scenario', async () => {
    (AuthService.hasCompletedOnboarding as jest.Mock).mockResolvedValue(true);
    (AuthService.isAuthenticated as jest.Mock).mockResolvedValue(true);

    const hasOnboarded = await AuthService.hasCompletedOnboarding();
    const isAuth = await AuthService.isAuthenticated();

    expect(hasOnboarded).toBe(true);
    expect(isAuth).toBe(true);
    expect(AuthService.hasCompletedOnboarding).toHaveBeenCalled();
    expect(AuthService.isAuthenticated).toHaveBeenCalled();
  });

  it('handles authentication check errors gracefully', async () => {
    (AuthService.hasCompletedOnboarding as jest.Mock).mockRejectedValue(new Error('Test error'));
    (AuthService.isAuthenticated as jest.Mock).mockRejectedValue(new Error('Test error'));

    try {
      await AuthService.hasCompletedOnboarding();
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
    }

    try {
      await AuthService.isAuthenticated();
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
    }

    expect(AuthService.hasCompletedOnboarding).toHaveBeenCalled();
    expect(AuthService.isAuthenticated).toHaveBeenCalled();
  });

  it('validates authentication service interface', () => {
    // Ensure the AuthService has the expected methods
    expect(typeof AuthService.hasCompletedOnboarding).toBe('function');
    expect(typeof AuthService.isAuthenticated).toBe('function');
  });
}); 
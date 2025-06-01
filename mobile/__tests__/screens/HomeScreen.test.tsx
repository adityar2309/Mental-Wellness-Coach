import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import HomeScreen from '../../src/screens/HomeScreen';
import { AuthService, User } from '../../src/services/AuthService';

// Mock dependencies
jest.mock('../../src/services/AuthService', () => ({
  AuthService: {
    getUserData: jest.fn(),
    logout: jest.fn(),
  },
}));

jest.mock('react-native', () => {
  const RN = jest.requireActual('react-native');
  return {
    ...RN,
    Alert: {
      alert: jest.fn(),
    },
  };
});

const mockNavigation = {
  navigate: jest.fn(),
  replace: jest.fn(),
} as any;

describe('HomeScreen', () => {
  const mockUser: User = {
    id: 'user-123',
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    created_at: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock current time for consistent greeting tests
    jest.spyOn(Date.prototype, 'getHours').mockReturnValue(10); // Morning
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders correctly with user data', async () => {
    (AuthService.getUserData as jest.Mock).mockResolvedValue(mockUser);

    const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(getByText('Good morning, testuser! 👋')).toBeTruthy();
      expect(getByText('How are you feeling today?')).toBeTruthy();
    });

    expect(getByText('Mood Check-In')).toBeTruthy();
    expect(getByText('Chat with AI')).toBeTruthy();
    expect(getByText('Analytics')).toBeTruthy();
    expect(getByText('Journal')).toBeTruthy();
    expect(getByText('Mindfulness')).toBeTruthy();
    expect(getByText('Crisis Help')).toBeTruthy();
  });

  it('renders correctly without user data', async () => {
    (AuthService.getUserData as jest.Mock).mockResolvedValue(null);

    const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(getByText('Good morning, there! 👋')).toBeTruthy();
    });
  });

  it('handles user data loading errors gracefully', async () => {
    (AuthService.getUserData as jest.Mock).mockRejectedValue(new Error('Failed to load'));
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error loading user data:', expect.any(Error));
    });

    consoleSpy.mockRestore();
  });

  describe('Greeting functionality', () => {
    it('shows morning greeting', async () => {
      jest.spyOn(Date.prototype, 'getHours').mockReturnValue(9);
      (AuthService.getUserData as jest.Mock).mockResolvedValue(mockUser);

      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        expect(getByText('Good morning, testuser! 👋')).toBeTruthy();
      });
    });

    it('shows afternoon greeting', async () => {
      jest.spyOn(Date.prototype, 'getHours').mockReturnValue(14);
      (AuthService.getUserData as jest.Mock).mockResolvedValue(mockUser);

      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        expect(getByText('Good afternoon, testuser! 👋')).toBeTruthy();
      });
    });

    it('shows evening greeting', async () => {
      jest.spyOn(Date.prototype, 'getHours').mockReturnValue(20);
      (AuthService.getUserData as jest.Mock).mockResolvedValue(mockUser);

      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        expect(getByText('Good evening, testuser! 👋')).toBeTruthy();
      });
    });
  });

  describe('Navigation', () => {
    beforeEach(async () => {
      (AuthService.getUserData as jest.Mock).mockResolvedValue(mockUser);
    });

    it('navigates to mood check-in when button pressed', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        const moodButton = getByText('Mood Check-In');
        fireEvent.press(moodButton);
      });

      expect(mockNavigation.navigate).toHaveBeenCalledWith('MoodCheckIn');
    });

    it('navigates to chat when button pressed', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        const chatButton = getByText('Chat with AI');
        fireEvent.press(chatButton);
      });

      expect(mockNavigation.navigate).toHaveBeenCalledWith('Chat');
    });

    it('navigates to profile when button pressed', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        const profileButton = getByText('View Profile');
        fireEvent.press(profileButton);
      });

      expect(mockNavigation.navigate).toHaveBeenCalledWith('Profile');
    });
  });

  describe('Logout functionality', () => {
    beforeEach(async () => {
      (AuthService.getUserData as jest.Mock).mockResolvedValue(mockUser);
      (AuthService.logout as jest.Mock).mockResolvedValue(undefined);
    });

    it('shows logout confirmation dialog', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        const logoutButton = getByText('Sign Out');
        fireEvent.press(logoutButton);
      });

      expect(Alert.alert).toHaveBeenCalledWith(
        'Sign Out',
        'Are you sure you want to sign out?',
        expect.arrayContaining([
          expect.objectContaining({ text: 'Cancel', style: 'cancel' }),
          expect.objectContaining({ 
            text: 'Sign Out', 
            style: 'destructive',
            onPress: expect.any(Function)
          }),
        ])
      );
    });

    it('handles logout confirmation', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        const logoutButton = getByText('Sign Out');
        fireEvent.press(logoutButton);
      });

      // Simulate user confirming logout
      const alertCall = (Alert.alert as jest.Mock).mock.calls[0];
      const confirmButton = alertCall[2][1]; // Second button (Sign Out)
      await confirmButton.onPress();

      expect(AuthService.logout).toHaveBeenCalled();
      expect(mockNavigation.replace).toHaveBeenCalledWith('Login');
    });

    it('handles logout cancellation', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        const logoutButton = getByText('Sign Out');
        fireEvent.press(logoutButton);
      });

      // Simulate user canceling logout
      const alertCall = (Alert.alert as jest.Mock).mock.calls[0];
      const cancelButton = alertCall[2][0]; // First button (Cancel)
      
      // Cancel button might not have onPress, so check if it exists
      if (cancelButton.onPress) {
        await cancelButton.onPress();
      }

      // Logout should not be called and navigation should not happen
      expect(AuthService.logout).not.toHaveBeenCalled();
      expect(mockNavigation.replace).not.toHaveBeenCalled();
    });
  });

  describe('Component structure', () => {
    beforeEach(async () => {
      (AuthService.getUserData as jest.Mock).mockResolvedValue(mockUser);
    });

    it('renders all main sections', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        // Header section
        expect(getByText('How are you feeling today?')).toBeTruthy();
        
        // Quick actions
        expect(getByText('Mood Check-In')).toBeTruthy();
        expect(getByText('Chat with AI')).toBeTruthy();
        
        // Features grid
        expect(getByText('Analytics')).toBeTruthy();
        expect(getByText('Journal')).toBeTruthy();
        expect(getByText('Mindfulness')).toBeTruthy();
        expect(getByText('Crisis Help')).toBeTruthy();
        
        // Profile section
        expect(getByText('View Profile')).toBeTruthy();
        expect(getByText('Sign Out')).toBeTruthy();
      });
    });

    it('displays correct action descriptions', async () => {
      const { getByText } = render(<HomeScreen navigation={mockNavigation} />);

      await waitFor(() => {
        expect(getByText('How are you feeling?')).toBeTruthy();
        expect(getByText('Get support & guidance')).toBeTruthy();
      });
    });
  });
}); 
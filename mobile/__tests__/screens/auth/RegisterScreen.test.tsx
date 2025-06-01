import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';
import RegisterScreen from '../../../src/screens/auth/RegisterScreen';
import { AuthService } from '../../../src/services/AuthService';

// Mock dependencies
jest.mock('../../../src/services/AuthService');
jest.mock('@react-navigation/stack');

// Mock Alert
jest.spyOn(Alert, 'alert').mockImplementation(() => {});

// Mock navigation
const mockNavigation = {
  navigate: jest.fn(),
  replace: jest.fn(),
  goBack: jest.fn(),
};

describe('RegisterScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('UI Rendering', () => {
    it('renders all required form elements', () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Check header elements
      expect(screen.getByText('🌟')).toBeTruthy();
      expect(screen.getByText('Create Your Account')).toBeTruthy();
      expect(screen.getByText('Join thousands on their mental wellness journey')).toBeTruthy();

      // Check form fields
      expect(screen.getByText('Full Name (Optional)')).toBeTruthy();
      expect(screen.getByText('Email Address *')).toBeTruthy();
      expect(screen.getByText('Password *')).toBeTruthy();
      expect(screen.getByText('Confirm Password *')).toBeTruthy();

      // Check placeholders
      expect(screen.getByPlaceholderText('Enter your full name')).toBeTruthy();
      expect(screen.getByPlaceholderText('Enter your email')).toBeTruthy();
      expect(screen.getByPlaceholderText('Create a password')).toBeTruthy();
      expect(screen.getByPlaceholderText('Confirm your password')).toBeTruthy();

      // Check buttons and links
      expect(screen.getByText('Create Account')).toBeTruthy();
      expect(screen.getByText('Already have an account?')).toBeTruthy();
      expect(screen.getByText('Sign In')).toBeTruthy();

      // Check privacy notice
      expect(screen.getByText(/Your mental health data is encrypted and secure/)).toBeTruthy();
    });

    it('renders input fields with correct properties', () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      const nameInput = screen.getByPlaceholderText('Enter your full name');
      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Create a password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');

      // Check input properties
      expect(emailInput.props.keyboardType).toBe('email-address');
      expect(emailInput.props.autoCapitalize).toBe('none');
      expect(passwordInput.props.secureTextEntry).toBe(true);
      expect(confirmPasswordInput.props.secureTextEntry).toBe(true);
      expect(nameInput.props.autoCapitalize).toBe('words');
    });
  });

  describe('Form Validation', () => {
    it('shows validation errors for empty required fields', async () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      const createButton = screen.getByText('Create Account');
      fireEvent.press(createButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
        expect(screen.getByText('Please confirm your password')).toBeTruthy();
      });
    });

    it('validates email format', async () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const createButton = screen.getByText('Create Account');

      fireEvent.changeText(emailInput, 'invalid-email');
      fireEvent.press(createButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeTruthy();
      });
    });

    it('validates password length', async () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      const passwordInput = screen.getByPlaceholderText('Create a password');
      const createButton = screen.getByText('Create Account');

      fireEvent.changeText(passwordInput, '123');
      fireEvent.press(createButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeTruthy();
      });
    });

    it('validates password confirmation match', async () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      const passwordInput = screen.getByPlaceholderText('Create a password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');
      const createButton = screen.getByText('Create Account');

      fireEvent.changeText(passwordInput, 'password123');
      fireEvent.changeText(confirmPasswordInput, 'differentpassword');
      fireEvent.press(createButton);

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeTruthy();
      });
    });

    it('clears errors when user types in fields', async () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const createButton = screen.getByText('Create Account');

      // Trigger validation error
      fireEvent.press(createButton);
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
      });

      // Type in email field to clear error
      fireEvent.changeText(emailInput, 'test@example.com');
      await waitFor(() => {
        expect(screen.queryByText('Email is required')).toBeNull();
      });
    });
  });

  describe('Form Submission', () => {
    const validFormData = {
      name: 'John Doe',
      email: 'john@example.com',
      password: 'password123',
      confirmPassword: 'password123',
    };

    it('submits form with valid data', async () => {
      const mockResponse = {
        user: { id: '1', name: 'John Doe', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Registration successful',
      };

      (AuthService.register as jest.Mock).mockResolvedValue(mockResponse);

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your full name'), validFormData.name);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validFormData.email);
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), validFormData.password);
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), validFormData.confirmPassword);

      // Submit form
      fireEvent.press(screen.getByText('Create Account'));

      await waitFor(() => {
        expect(AuthService.register).toHaveBeenCalledWith({
          name: validFormData.name,
          email: validFormData.email,
          password: validFormData.password,
        });
      });
    });

    it('shows loading state during submission', async () => {
      (AuthService.register as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill form with valid data
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validFormData.email);
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), validFormData.password);
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), validFormData.confirmPassword);

      // Submit form
      fireEvent.press(screen.getByText('Create Account'));

      // Check loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });
    });

    it('shows success alert and navigates on successful registration', async () => {
      const mockResponse = {
        user: { id: '1', name: 'John Doe', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Registration successful',
      };

      (AuthService.register as jest.Mock).mockResolvedValue(mockResponse);

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validFormData.email);
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), validFormData.password);
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), validFormData.confirmPassword);
      fireEvent.press(screen.getByText('Create Account'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Welcome to Mental Wellness Coach!',
          "Hello John Doe! Your account has been created successfully. Let's start your wellness journey!",
          expect.any(Array)
        );
      });
    });

    it('handles registration without name gracefully', async () => {
      const mockResponse = {
        user: { id: '1', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Registration successful',
      };

      (AuthService.register as jest.Mock).mockResolvedValue(mockResponse);

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill form without name
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validFormData.email);
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), validFormData.password);
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), validFormData.confirmPassword);
      fireEvent.press(screen.getByText('Create Account'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Welcome to Mental Wellness Coach!',
          "Hello there! Your account has been created successfully. Let's start your wellness journey!",
          expect.any(Array)
        );
      });
    });
  });

  describe('Error Handling', () => {
    const validFormData = {
      email: 'john@example.com',
      password: 'password123',
      confirmPassword: 'password123',
    };

    it('shows error alert on registration failure', async () => {
      const errorMessage = 'User already exists';
      (AuthService.register as jest.Mock).mockRejectedValue(new Error(errorMessage));

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validFormData.email);
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), validFormData.password);
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), validFormData.confirmPassword);
      fireEvent.press(screen.getByText('Create Account'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Registration Failed',
          errorMessage,
          [{ text: 'OK' }]
        );
      });
    });

    it('shows generic error message for unknown errors', async () => {
      (AuthService.register as jest.Mock).mockRejectedValue('Unknown error');

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validFormData.email);
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), validFormData.password);
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), validFormData.confirmPassword);
      fireEvent.press(screen.getByText('Create Account'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Registration Failed',
          'Please try again later.',
          [{ text: 'OK' }]
        );
      });
    });
  });

  describe('Navigation', () => {
    it('navigates back when sign in link is pressed', () => {
      render(<RegisterScreen navigation={mockNavigation as any} />);

      const signInLink = screen.getByText('Sign In');
      fireEvent.press(signInLink);

      expect(mockNavigation.goBack).toHaveBeenCalled();
    });

    it('navigates to Home on successful registration', async () => {
      const mockResponse = {
        user: { id: '1', name: 'John Doe', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Registration successful',
      };

      (AuthService.register as jest.Mock).mockResolvedValue(mockResponse);

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), 'john@example.com');
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), 'password123');
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), 'password123');
      fireEvent.press(screen.getByText('Create Account'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalled();
      });

      // Simulate alert button press
      const alertCall = (Alert.alert as jest.Mock).mock.calls[0];
      const alertButtons = alertCall[2];
      const getStartedButton = alertButtons[0];
      getStartedButton.onPress();

      expect(mockNavigation.replace).toHaveBeenCalledWith('Home');
    });
  });

  describe('Accessibility', () => {
    it('disables form during loading', async () => {
      (AuthService.register as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      render(<RegisterScreen navigation={mockNavigation as any} />);

      // Fill form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), 'john@example.com');
      fireEvent.changeText(screen.getByPlaceholderText('Create a password'), 'password123');
      fireEvent.changeText(screen.getByPlaceholderText('Confirm your password'), 'password123');

      // Submit form
      fireEvent.press(screen.getByText('Create Account'));

      await waitFor(() => {
        // Check that inputs are disabled
        expect(screen.getByPlaceholderText('Enter your full name').props.editable).toBe(false);
        expect(screen.getByPlaceholderText('Enter your email').props.editable).toBe(false);
        expect(screen.getByPlaceholderText('Create a password').props.editable).toBe(false);
        expect(screen.getByPlaceholderText('Confirm your password').props.editable).toBe(false);
      });
    });
  });
}); 
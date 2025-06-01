import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';
import LoginScreen from '../../../src/screens/auth/LoginScreen';
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

describe('LoginScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('UI Rendering', () => {
    it('renders all required form elements', () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      // Check header elements
      expect(screen.getByText('🤗')).toBeTruthy();
      expect(screen.getByText('Welcome Back')).toBeTruthy();
      expect(screen.getByText('Sign in to continue your mental wellness journey')).toBeTruthy();

      // Check form fields
      expect(screen.getByText('Email Address')).toBeTruthy();
      expect(screen.getByText('Password')).toBeTruthy();

      // Check placeholders
      expect(screen.getByPlaceholderText('Enter your email')).toBeTruthy();
      expect(screen.getByPlaceholderText('Enter your password')).toBeTruthy();

      // Check buttons and links
      expect(screen.getByText('Sign In')).toBeTruthy();
      expect(screen.getByText("Don't have an account?")).toBeTruthy();
      expect(screen.getByText('Sign Up')).toBeTruthy();

      // Check crisis support
      expect(screen.getByText(/In crisis\? Call 988 for immediate support/)).toBeTruthy();
    });

    it('renders input fields with correct properties', () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');

      // Check input properties
      expect(emailInput.props.keyboardType).toBe('email-address');
      expect(emailInput.props.autoCapitalize).toBe('none');
      expect(emailInput.props.autoCorrect).toBe(false);
      expect(passwordInput.props.secureTextEntry).toBe(true);
      expect(passwordInput.props.autoCapitalize).toBe('none');
      expect(passwordInput.props.autoCorrect).toBe(false);
    });
  });

  describe('Form Validation', () => {
    it('shows validation errors for empty required fields', async () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const signInButton = screen.getByText('Sign In');
      fireEvent.press(signInButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });
    });

    it('validates email format', async () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const signInButton = screen.getByText('Sign In');

      fireEvent.changeText(emailInput, 'invalid-email');
      fireEvent.press(signInButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeTruthy();
      });
    });

    it('accepts valid email format', async () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByText('Sign In');

      fireEvent.changeText(emailInput, 'valid@example.com');
      fireEvent.changeText(passwordInput, 'password123');
      fireEvent.press(signInButton);

      await waitFor(() => {
        expect(screen.queryByText('Please enter a valid email address')).toBeNull();
        expect(screen.queryByText('Email is required')).toBeNull();
        expect(screen.queryByText('Password is required')).toBeNull();
      });
    });

    it('clears errors when user types in fields', async () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const signInButton = screen.getByText('Sign In');

      // Trigger validation errors
      fireEvent.press(signInButton);
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });

      // Type in email field to clear error
      fireEvent.changeText(emailInput, 'test@example.com');
      await waitFor(() => {
        expect(screen.queryByText('Email is required')).toBeNull();
      });

      // Type in password field to clear error
      fireEvent.changeText(passwordInput, 'password123');
      await waitFor(() => {
        expect(screen.queryByText('Password is required')).toBeNull();
      });
    });
  });

  describe('Form Submission', () => {
    const validCredentials = {
      email: 'john@example.com',
      password: 'password123',
    };

    it('submits form with valid credentials', async () => {
      const mockResponse = {
        user: { id: '1', name: 'John Doe', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Login successful',
      };

      (AuthService.login as jest.Mock).mockResolvedValue(mockResponse);

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validCredentials.email);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), validCredentials.password);

      // Submit form
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(AuthService.login).toHaveBeenCalledWith({
          email: validCredentials.email,
          password: validCredentials.password,
        });
      });
    });

    it('shows loading state during submission', async () => {
      (AuthService.login as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill form with valid data
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validCredentials.email);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), validCredentials.password);

      // Submit form
      fireEvent.press(screen.getByText('Sign In'));

      // Check loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });
    });

    it('shows success alert and navigates on successful login', async () => {
      const mockResponse = {
        user: { id: '1', name: 'John Doe', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Login successful',
      };

      (AuthService.login as jest.Mock).mockResolvedValue(mockResponse);

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validCredentials.email);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), validCredentials.password);
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Welcome Back!',
          "Hello John Doe! Ready to continue your wellness journey?",
          expect.any(Array)
        );
      });
    });

    it('handles login without user name gracefully', async () => {
      const mockResponse = {
        user: { id: '1', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Login successful',
      };

      (AuthService.login as jest.Mock).mockResolvedValue(mockResponse);

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validCredentials.email);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), validCredentials.password);
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Welcome Back!',
          "Hello there! Ready to continue your wellness journey?",
          expect.any(Array)
        );
      });
    });

    it('does not submit form with invalid data', async () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      // Try to submit without filling form
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(AuthService.login).not.toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    const validCredentials = {
      email: 'john@example.com',
      password: 'password123',
    };

    it('shows error alert on login failure', async () => {
      const errorMessage = 'Invalid credentials';
      (AuthService.login as jest.Mock).mockRejectedValue(new Error(errorMessage));

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validCredentials.email);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), validCredentials.password);
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Login Failed',
          errorMessage,
          [{ text: 'OK' }]
        );
      });
    });

    it('shows generic error message for unknown errors', async () => {
      (AuthService.login as jest.Mock).mockRejectedValue('Network error');

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validCredentials.email);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), validCredentials.password);
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Login Failed',
          'Please check your credentials and try again.',
          [{ text: 'OK' }]
        );
      });
    });

    it('handles network timeout errors', async () => {
      (AuthService.login as jest.Mock).mockRejectedValue(new Error('Request timeout'));

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), validCredentials.email);
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), validCredentials.password);
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Login Failed',
          'Request timeout',
          [{ text: 'OK' }]
        );
      });
    });
  });

  describe('Navigation', () => {
    it('navigates to Register screen when sign up link is pressed', () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const signUpLink = screen.getByText('Sign Up');
      fireEvent.press(signUpLink);

      expect(mockNavigation.navigate).toHaveBeenCalledWith('Register');
    });

    it('navigates to Home on successful login', async () => {
      const mockResponse = {
        user: { id: '1', name: 'John Doe', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Login successful',
      };

      (AuthService.login as jest.Mock).mockResolvedValue(mockResponse);

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), 'john@example.com');
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), 'password123');
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalled();
      });

      // Simulate alert button press
      const alertCall = (Alert.alert as jest.Mock).mock.calls[0];
      const alertButtons = alertCall[2];
      const letsGoButton = alertButtons[0];
      letsGoButton.onPress();

      expect(mockNavigation.replace).toHaveBeenCalledWith('Home');
    });
  });

  describe('Accessibility', () => {
    it('disables form during loading', async () => {
      (AuthService.login as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), 'john@example.com');
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), 'password123');

      // Submit form
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        // Check that inputs are disabled
        expect(screen.getByPlaceholderText('Enter your email').props.editable).toBe(false);
        expect(screen.getByPlaceholderText('Enter your password').props.editable).toBe(false);
        // Check that navigation is disabled
        expect(screen.getByText('Sign Up').props.disabled).toBe(true);
      });
    });

    it('disables sign in button during loading', async () => {
      (AuthService.login as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), 'john@example.com');
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), 'password123');
      fireEvent.press(screen.getByText('Sign In'));

      await waitFor(() => {
        // Check that sign in button is disabled
        const signInButton = screen.getByText('Sign In').parent;
        expect(signInButton?.props.disabled).toBe(true);
      });
    });
  });

  describe('Security Features', () => {
    it('hides password input text', () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const passwordInput = screen.getByPlaceholderText('Enter your password');
      expect(passwordInput.props.secureTextEntry).toBe(true);
    });

    it('disables autocorrect for sensitive fields', () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');

      expect(emailInput.props.autoCorrect).toBe(false);
      expect(passwordInput.props.autoCorrect).toBe(false);
    });

    it('uses appropriate keyboard type for email', () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      expect(emailInput.props.keyboardType).toBe('email-address');
    });
  });

  describe('Crisis Support Feature', () => {
    it('displays crisis support information prominently', () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const crisisText = screen.getByText(/In crisis\? Call 988 for immediate support/);
      expect(crisisText).toBeTruthy();
      
      // Verify it's in a visually distinct container
      expect(crisisText.parent?.props.style).toMatchObject(
        expect.objectContaining({
          backgroundColor: '#fef2f2',
        })
      );
    });
  });

  describe('Form State Management', () => {
    it('maintains form state during user interaction', async () => {
      render(<LoginScreen navigation={mockNavigation as any} />);

      const emailInput = screen.getByPlaceholderText('Enter your email');
      const passwordInput = screen.getByPlaceholderText('Enter your password');

      // Type in email
      fireEvent.changeText(emailInput, 'test@example.com');
      expect(emailInput.props.value).toBe('test@example.com');

      // Type in password
      fireEvent.changeText(passwordInput, 'mypassword');
      expect(passwordInput.props.value).toBe('mypassword');

      // Verify state is maintained
      expect(emailInput.props.value).toBe('test@example.com');
    });

    it('resets loading state after form submission', async () => {
      const mockResponse = {
        user: { id: '1', name: 'John Doe', email: 'john@example.com' },
        token: 'mock-token',
        message: 'Login successful',
      };

      (AuthService.login as jest.Mock).mockResolvedValue(mockResponse);

      render(<LoginScreen navigation={mockNavigation as any} />);

      // Fill and submit form
      fireEvent.changeText(screen.getByPlaceholderText('Enter your email'), 'john@example.com');
      fireEvent.changeText(screen.getByPlaceholderText('Enter your password'), 'password123');
      fireEvent.press(screen.getByText('Sign In'));

      // Wait for completion
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalled();
      });

      // Check that loading state is reset
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Enter your email').props.editable).toBe(true);
        expect(screen.getByPlaceholderText('Enter your password').props.editable).toBe(true);
      });
    });
  });
}); 
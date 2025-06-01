/**
 * Mental Wellness Coach - ChatScreen Integration Tests
 * 
 * Comprehensive test suite for the ChatScreen component covering
 * user interactions, messaging flow, and crisis detection UI.
 */

import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react-native';
import { Alert } from 'react-native';
import ChatScreen from '../../src/screens/chat/ChatScreen';
import ChatService from '../../src/services/ChatService';

// Mock navigation
const mockNavigate = jest.fn();
const mockNavigation = {
  navigate: mockNavigate,
  goBack: jest.fn(),
  setOptions: jest.fn(),
};

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => mockNavigation,
}));

// Mock ChatService
jest.mock('../../src/services/ChatService');
const MockedChatService = ChatService as jest.MockedClass<typeof ChatService>;

// Mock Alert
jest.spyOn(Alert, 'alert');

describe('ChatScreen', () => {
  let mockChatService: jest.Mocked<ChatService>;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Create mock chat service instance
    mockChatService = new MockedChatService() as jest.Mocked<ChatService>;
    
    // Override the useRef to return our mock
    const useRefSpy = jest.spyOn(React, 'useRef');
    useRefSpy.mockReturnValue({ current: mockChatService });

    // Setup default mock implementations
    mockChatService.isAuthenticated.mockResolvedValue(true);
    mockChatService.isCrisisDetected.mockReturnValue(false);
    mockChatService.getCrisisSupportMessage.mockReturnValue('');
  });

  describe('Initialization', () => {
    it('should render loading state initially', async () => {
      // Arrange
      mockChatService.isAuthenticated.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(true), 100))
      );

      // Act
      render(<ChatScreen />);

      // Assert
      expect(screen.getByText('Starting chat...')).toBeTruthy();
      expect(screen.getByTestId('activity-indicator')).toBeTruthy();
    });

    it('should initialize with welcome message for authenticated user', async () => {
      // Arrange
      mockChatService.isAuthenticated.mockResolvedValue(true);

      // Act
      render(<ChatScreen />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText("Hi! I'm your AI wellness coach. I'm here to support you through any challenges you might be facing. How are you feeling today?")).toBeTruthy();
      });
    });

    it('should show error for unauthenticated user', async () => {
      // Arrange
      mockChatService.isAuthenticated.mockResolvedValue(false);

      // Act
      render(<ChatScreen />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Please log in to start chatting')).toBeTruthy();
      });
    });

    it('should handle initialization errors gracefully', async () => {
      // Arrange
      mockChatService.isAuthenticated.mockRejectedValue(new Error('Network error'));

      // Act
      render(<ChatScreen />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Failed to initialize chat. Please try again.')).toBeTruthy();
      });
    });
  });

  describe('Message Sending', () => {
    beforeEach(async () => {
      mockChatService.isAuthenticated.mockResolvedValue(true);
      render(<ChatScreen />);
      
      // Wait for initialization to complete
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type your message...')).toBeTruthy();
      });
    });

    it('should send message successfully', async () => {
      // Arrange
      const testMessage = 'I need help with anxiety';
      const mockResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'I understand you\'re dealing with anxiety. Let me help you.',
          crisis_level: 'NONE',
        },
        message_id: 'msg_456',
      };
      
      mockChatService.sendMessage.mockResolvedValue(mockResponse);

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, testMessage);
      fireEvent.press(sendButton);

      // Assert
      expect(screen.getByText(testMessage)).toBeTruthy();
      
      await waitFor(() => {
        expect(mockChatService.sendMessage).toHaveBeenCalledWith({
          message: testMessage,
          conversation_id: undefined,
        });
        expect(screen.getByText('I understand you\'re dealing with anxiety. Let me help you.')).toBeTruthy();
      });
    });

    it('should clear input after sending message', async () => {
      // Arrange
      const testMessage = 'Test message';
      const mockResponse = {
        conversation_id: 'conv_123',
        response: { text: 'Response' },
        message_id: 'msg_456',
      };
      
      mockChatService.sendMessage.mockResolvedValue(mockResponse);

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, testMessage);
      fireEvent.press(sendButton);

      // Assert
      await waitFor(() => {
        expect(textInput.props.value).toBe('');
      });
    });

    it('should disable send button when no text is entered', () => {
      // Act
      const sendButton = screen.getByText('Send');

      // Assert
      expect(sendButton.props.accessibilityState?.disabled).toBe(true);
    });

    it('should enable send button when text is entered', () => {
      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, 'Test message');

      // Assert
      expect(sendButton.props.accessibilityState?.disabled).toBe(false);
    });

    it('should handle message sending errors', async () => {
      // Arrange
      const testMessage = 'Test message';
      mockChatService.sendMessage.mockRejectedValue(new Error('Network error'));

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, testMessage);
      fireEvent.press(sendButton);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Failed to send message. Please try again.')).toBeTruthy();
        expect(screen.getByText("I'm sorry, I'm having trouble responding right now. Please try again in a moment.")).toBeTruthy();
      });
    });
  });

  describe('Crisis Detection', () => {
    beforeEach(async () => {
      mockChatService.isAuthenticated.mockResolvedValue(true);
      render(<ChatScreen />);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type your message...')).toBeTruthy();
      });
    });

    it('should show crisis alert for high-risk messages', async () => {
      // Arrange
      const crisisResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'I understand you\'re in crisis.',
          crisis_level: 'HIGH',
          suggested_actions: ['Contact crisis hotline', 'Reach out to friend'],
        },
        message_id: 'msg_456',
      };

      mockChatService.sendMessage.mockResolvedValue(crisisResponse);
      mockChatService.isCrisisDetected.mockReturnValue(true);
      mockChatService.getCrisisSupportMessage.mockReturnValue(
        'I want to make sure you\'re safe. Let\'s talk about getting you some support.'
      );

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, 'I want to hurt myself');
      fireEvent.press(sendButton);

      // Assert
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Support Available',
          'I want to make sure you\'re safe. Let\'s talk about getting you some support.',
          expect.any(Array)
        );
      });
    });

    it('should show crisis resources when user requests help', async () => {
      // Arrange
      const crisisResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'I understand you\'re in crisis.',
          crisis_level: 'CRITICAL',
          suggested_actions: ['Contact emergency services', 'Go to emergency room'],
          safety_resources: [{ name: 'Crisis Hotline', phone: '988' }],
        },
        message_id: 'msg_456',
      };

      mockChatService.sendMessage.mockResolvedValue(crisisResponse);
      mockChatService.isCrisisDetected.mockReturnValue(true);

      // Mock Alert.alert to capture the callback
      const mockAlert = Alert.alert as jest.Mock;
      mockAlert.mockImplementation((title, message, buttons) => {
        // Simulate user pressing "Get Help Resources" button
        const helpButton = buttons?.find((b: any) => b.text === 'Get Help Resources');
        if (helpButton) {
          helpButton.onPress();
        }
      });

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, 'I want to hurt myself');
      fireEvent.press(sendButton);

      // Assert
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledTimes(2); // First for crisis alert, second for resources
        expect(mockAlert).toHaveBeenLastCalledWith(
          'Crisis Support Resources',
          expect.stringContaining('National Suicide Prevention Lifeline: 988'),
          [{ text: 'Close', style: 'default' }]
        );
      });
    });

    it('should not show crisis alert for normal messages', async () => {
      // Arrange
      const normalResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'How are you feeling today?',
          crisis_level: 'NONE',
        },
        message_id: 'msg_456',
      };

      mockChatService.sendMessage.mockResolvedValue(normalResponse);
      mockChatService.isCrisisDetected.mockReturnValue(false);

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, 'How are you?');
      fireEvent.press(sendButton);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('How are you feeling today?')).toBeTruthy();
      });
      
      expect(Alert.alert).not.toHaveBeenCalled();
    });
  });

  describe('UI Behavior', () => {
    beforeEach(async () => {
      mockChatService.isAuthenticated.mockResolvedValue(true);
      render(<ChatScreen />);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type your message...')).toBeTruthy();
      });
    });

    it('should show typing indicator while processing message', async () => {
      // Arrange
      let resolvePromise: (value: any) => void;
      const messagePromise = new Promise(resolve => {
        resolvePromise = resolve;
      });
      
      mockChatService.sendMessage.mockReturnValue(messagePromise);

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, 'Test message');
      fireEvent.press(sendButton);

      // Assert - typing indicator should be visible
      expect(screen.getByText('AI is typing...')).toBeTruthy();
      expect(screen.getByText('Thinking...')).toBeTruthy(); // Header subtitle

      // Complete the promise
      resolvePromise!({
        conversation_id: 'conv_123',
        response: { text: 'Response' },
        message_id: 'msg_456',
      });

      // Assert - typing indicator should be gone
      await waitFor(() => {
        expect(screen.queryByText('AI is typing...')).toBeNull();
        expect(screen.getByText('Here to help')).toBeTruthy(); // Header subtitle back to normal
      });
    });

    it('should display proper header information', () => {
      // Assert
      expect(screen.getByText('AI Wellness Coach')).toBeTruthy();
      expect(screen.getByText('Here to help')).toBeTruthy();
    });

    it('should prevent sending empty messages', () => {
      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      fireEvent.changeText(textInput, '   '); // Only whitespace
      fireEvent.press(sendButton);

      // Assert
      expect(mockChatService.sendMessage).not.toHaveBeenCalled();
    });

    it('should limit message length', () => {
      // Arrange
      const longMessage = 'a'.repeat(1001); // Over 1000 character limit

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      fireEvent.changeText(textInput, longMessage);

      // Assert
      expect(textInput.props.value.length).toBeLessThanOrEqual(1000);
    });
  });

  describe('Accessibility', () => {
    beforeEach(async () => {
      mockChatService.isAuthenticated.mockResolvedValue(true);
      render(<ChatScreen />);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Type your message...')).toBeTruthy();
      });
    });

    it('should have proper accessibility labels', () => {
      // Assert
      const textInput = screen.getByPlaceholderText('Type your message...');
      const sendButton = screen.getByText('Send');

      expect(textInput.props.accessibilityLabel).toBeDefined();
      expect(sendButton.props.accessibilityRole).toBeDefined();
    });

    it('should support submit on return key', async () => {
      // Arrange
      const mockResponse = {
        conversation_id: 'conv_123',
        response: { text: 'Response' },
        message_id: 'msg_456',
      };
      mockChatService.sendMessage.mockResolvedValue(mockResponse);

      // Act
      const textInput = screen.getByPlaceholderText('Type your message...');
      fireEvent.changeText(textInput, 'Test message');
      fireEvent(textInput, 'submitEditing');

      // Assert
      await waitFor(() => {
        expect(mockChatService.sendMessage).toHaveBeenCalled();
      });
    });
  });
}); 
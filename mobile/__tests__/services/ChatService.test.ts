/**
 * Mental Wellness Coach - ChatService Tests
 * 
 * Comprehensive test suite for the ChatService class covering
 * message sending, conversation management, and crisis detection.
 */

import ChatService, { ChatMessage, ChatResponse, SendMessageRequest } from '../../src/services/ChatService';

// Mock the dependencies
jest.mock('../../src/services/ApiClient', () => ({
  ApiClient: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    patch: jest.fn(),
    setBaseURL: jest.fn(),
  },
}));

jest.mock('../../src/services/AuthService', () => ({
  AuthService: {
    isAuthenticated: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
    getToken: jest.fn(),
    getCurrentUser: jest.fn(),
    storeToken: jest.fn(),
    storeUserData: jest.fn(),
    getUserData: jest.fn(),
    register: jest.fn(),
    markOnboardingCompleted: jest.fn(),
    hasCompletedOnboarding: jest.fn(),
    refreshUserData: jest.fn(),
  },
}));

// Import mocked modules
import { ApiClient } from '../../src/services/ApiClient';
import { AuthService } from '../../src/services/AuthService';

const mockApiClient = ApiClient as jest.Mocked<typeof ApiClient>;
const mockAuthService = AuthService as jest.Mocked<typeof AuthService>;

describe('ChatService', () => {
  let chatService: ChatService;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Create ChatService instance
    chatService = new ChatService();
  });

  describe('sendMessage', () => {
    it('should send a message successfully', async () => {
      // Arrange
      const messageData: SendMessageRequest = {
        message: 'Hello, I need some support',
        conversation_id: 'conv_123',
      };

      const expectedResponse: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'Hello! I\'m here to help. How are you feeling?',
          crisis_level: 'NONE',
          confidence: 0.95,
          conversation_tags: ['greeting', 'support'],
        },
        message_id: 'msg_456',
      };

      mockApiClient.post.mockResolvedValue(expectedResponse);

      // Act
      const result = await chatService.sendMessage(messageData);

      // Assert
      expect(mockApiClient.post).toHaveBeenCalledWith('/conversation/chat', messageData);
      expect(result).toEqual(expectedResponse);
    });

    it('should handle API errors gracefully', async () => {
      // Arrange
      const messageData: SendMessageRequest = {
        message: 'Test message',
      };

      const apiError = new Error('Network error');
      mockApiClient.post.mockRejectedValue(apiError);

      // Act & Assert
      await expect(chatService.sendMessage(messageData)).rejects.toThrow('Network error');
      expect(mockApiClient.post).toHaveBeenCalledWith('/conversation/chat', messageData);
    });

    it('should handle API errors with custom message', async () => {
      // Arrange
      const messageData: SendMessageRequest = {
        message: 'Test message',
      };

      const apiError = { message: 'Server unavailable' };
      mockApiClient.post.mockRejectedValue(apiError);

      // Act & Assert
      await expect(chatService.sendMessage(messageData)).rejects.toThrow('Server unavailable');
    });
  });

  describe('getConversationHistory', () => {
    it('should retrieve conversation history successfully', async () => {
      // Arrange
      const conversationId = 'conv_123';
      const expectedHistory = {
        conversation_id: conversationId,
        messages: [
          {
            id: 'msg_1',
            role: 'user' as const,
            content: 'Hello',
            timestamp: '2024-12-01T10:00:00Z',
          },
          {
            id: 'msg_2',
            role: 'assistant' as const,
            content: 'Hi! How can I help?',
            timestamp: '2024-12-01T10:01:00Z',
          },
        ],
        total_messages: 2,
      };

      mockApiClient.get.mockResolvedValue(expectedHistory);

      // Act
      const result = await chatService.getConversationHistory(conversationId);

      // Assert
      expect(mockApiClient.get).toHaveBeenCalledWith(`/conversation/history/${conversationId}`);
      expect(result).toEqual(expectedHistory);
    });

    it('should handle conversation not found error', async () => {
      // Arrange
      const conversationId = 'nonexistent';
      const apiError = new Error('Conversation not found');
      mockApiClient.get.mockRejectedValue(apiError);

      // Act & Assert
      await expect(chatService.getConversationHistory(conversationId))
        .rejects.toThrow('Conversation not found');
    });
  });

  describe('getUserConversations', () => {
    it('should retrieve user conversations successfully', async () => {
      // Arrange
      const expectedConversations = {
        conversations: [
          {
            id: 'conv_1',
            created_at: '2024-12-01T09:00:00Z',
            last_message_at: '2024-12-01T10:00:00Z',
            message_count: 5,
            latest_message: {
              id: 'msg_5',
              role: 'assistant' as const,
              content: 'Take care!',
              timestamp: '2024-12-01T10:00:00Z',
            },
          },
        ],
      };

      mockApiClient.get.mockResolvedValue(expectedConversations);

      // Act
      const result = await chatService.getUserConversations();

      // Assert
      expect(mockApiClient.get).toHaveBeenCalledWith('/conversation/conversations');
      expect(result).toEqual(expectedConversations.conversations);
    });

    it('should return empty array when no conversations response', async () => {
      // Arrange
      mockApiClient.get.mockResolvedValue({});

      // Act
      const result = await chatService.getUserConversations();

      // Assert
      expect(result).toEqual([]);
    });
  });

  describe('startNewConversation', () => {
    it('should start a new conversation successfully', async () => {
      // Arrange
      const expectedResponse = { conversation_id: 'conv_new_123' };
      mockApiClient.post.mockResolvedValue(expectedResponse);

      // Act
      const result = await chatService.startNewConversation();

      // Assert
      expect(mockApiClient.post).toHaveBeenCalledWith('/conversation/start', {});
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when user is authenticated', async () => {
      // Arrange
      mockAuthService.isAuthenticated.mockResolvedValue(true);

      // Act
      const result = await chatService.isAuthenticated();

      // Assert
      expect(mockAuthService.isAuthenticated).toHaveBeenCalled();
      expect(result).toBe(true);
    });

    it('should return false when authentication fails', async () => {
      // Arrange
      mockAuthService.isAuthenticated.mockRejectedValue(new Error('Auth error'));

      // Act
      const result = await chatService.isAuthenticated();

      // Assert
      expect(mockAuthService.isAuthenticated).toHaveBeenCalled();
      expect(result).toBe(false);
    });
  });

  describe('formatMessageTime', () => {
    beforeEach(() => {
      // Mock the current time to be December 1, 2024, 12:00:00 UTC
      jest.useFakeTimers();
      jest.setSystemTime(new Date('2024-12-01T12:00:00Z'));
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should return "Just now" for very recent messages', () => {
      // Arrange
      const timestamp = '2024-12-01T11:59:30Z'; // 30 seconds ago

      // Act
      const result = chatService.formatMessageTime(timestamp);

      // Assert
      expect(result).toBe('Just now');
    });

    it('should return minutes ago for recent messages', () => {
      // Arrange
      const timestamp = '2024-12-01T11:45:00Z'; // 15 minutes ago

      // Act
      const result = chatService.formatMessageTime(timestamp);

      // Assert
      expect(result).toBe('15 min ago');
    });

    it('should return hours ago for messages within a day', () => {
      // Arrange
      const timestamp = '2024-12-01T09:00:00Z'; // 3 hours ago

      // Act
      const result = chatService.formatMessageTime(timestamp);

      // Assert
      expect(result).toBe('3h ago');
    });

    it('should return days ago for messages within a week', () => {
      // Arrange
      const timestamp = '2024-11-29T12:00:00Z'; // 2 days ago

      // Act
      const result = chatService.formatMessageTime(timestamp);

      // Assert
      expect(result).toBe('2d ago');
    });

    it('should return formatted date for older messages', () => {
      // Arrange
      const timestamp = '2024-11-20T12:00:00Z'; // More than a week ago

      // Act
      const result = chatService.formatMessageTime(timestamp);

      // Assert
      expect(result).toBe('11/20/2024'); // US locale date format
    });

    it('should handle invalid timestamps gracefully', () => {
      // Arrange
      const invalidTimestamp = 'invalid-date';

      // Act
      const result = chatService.formatMessageTime(invalidTimestamp);

      // Assert
      expect(result).toBe('Unknown time');
    });
  });

  describe('isCrisisDetected', () => {
    it('should detect high crisis level', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'I understand you\'re in crisis. Let me help.',
          crisis_level: 'HIGH',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.isCrisisDetected(response);

      // Assert
      expect(result).toBe(true);
    });

    it('should detect critical crisis level', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'This requires immediate attention.',
          crisis_level: 'CRITICAL',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.isCrisisDetected(response);

      // Assert
      expect(result).toBe(true);
    });

    it('should not detect low crisis levels', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'How are you feeling?',
          crisis_level: 'LOW',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.isCrisisDetected(response);

      // Assert
      expect(result).toBe(false);
    });

    it('should not detect when no crisis level is provided', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'How are you feeling?',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.isCrisisDetected(response);

      // Assert
      expect(result).toBe(false);
    });
  });

  describe('getCrisisSupportMessage', () => {
    it('should return critical crisis message', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'I understand.',
          crisis_level: 'CRITICAL',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.getCrisisSupportMessage(response);

      // Assert
      expect(result).toBe('I notice you might be in crisis. Please consider reaching out for immediate support.');
    });

    it('should return high crisis message', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'I understand.',
          crisis_level: 'HIGH',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.getCrisisSupportMessage(response);

      // Assert
      expect(result).toBe('I want to make sure you\'re safe. Let\'s talk about getting you some support.');
    });

    it('should return generic message for other crisis levels', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'I understand.',
          crisis_level: 'MEDIUM',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.getCrisisSupportMessage(response);

      // Assert
      expect(result).toBe('I\'m here to support you through this difficult time.');
    });

    it('should return empty string for non-crisis responses', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'How are you feeling?',
          crisis_level: 'LOW',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.getCrisisSupportMessage(response);

      // Assert
      expect(result).toBe('');
    });

    it('should return empty string when no crisis level', () => {
      // Arrange
      const response: ChatResponse = {
        conversation_id: 'conv_123',
        response: {
          text: 'How are you feeling?',
        },
        message_id: 'msg_456',
      };

      // Act
      const result = chatService.getCrisisSupportMessage(response);

      // Assert
      expect(result).toBe('');
    });
  });
}); 
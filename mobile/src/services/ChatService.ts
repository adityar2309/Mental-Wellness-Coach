/**
 * Mental Wellness Coach - Chat Service
 * 
 * Service for handling AI chat conversations, message management,
 * and conversation history with crisis detection support.
 */

import { ApiClient } from './ApiClient';
import { AuthService } from './AuthService';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ConversationPreview {
  id: string;
  created_at: string;
  last_message_at: string;
  message_count: number;
  latest_message?: ChatMessage;
}

export interface ChatResponse {
  conversation_id: string;
  response: {
    text: string;
    crisis_level?: string;
    confidence?: number;
    suggested_actions?: string[];
    conversation_tags?: string[];
    safety_resources?: any[];
    risk_factors?: string[];
    escalation_needed?: boolean;
  };
  message_id: string;
}

export interface ConversationHistory {
  conversation_id: string;
  messages: ChatMessage[];
  total_messages: number;
}

export interface SendMessageRequest {
  message: string;
  conversation_id?: string;
}

export class ChatService {
  constructor() {
    // Removed: this.authService = new AuthService();
  }

  /**
   * Send a message to the AI and get a response.
   * 
   * Args:
   *   messageData: Object containing message content and optional conversation_id
   * 
   * Returns:
   *   Promise<ChatResponse>: AI response with conversation details
   */
  async sendMessage(messageData: SendMessageRequest): Promise<ChatResponse> {
    try {
      const response = await ApiClient.post('/conversations/chat', messageData);
      return response;
    } catch (error: any) {
      console.error('[ChatService] Failed to send message:', error);
      throw new Error(error.message || 'Failed to send message');
    }
  }

  /**
   * Get conversation history for a specific conversation.
   * 
   * Args:
   *   conversationId: ID of the conversation to retrieve
   * 
   * Returns:
   *   Promise<ConversationHistory>: Complete conversation history
   */
  async getConversationHistory(conversationId: string): Promise<ConversationHistory> {
    try {
      const response = await ApiClient.get(`/conversations/history/${conversationId}`);
      return response;
    } catch (error: any) {
      console.error('[ChatService] Failed to get conversation history:', error);
      throw new Error(error.message || 'Failed to get conversation history');
    }
  }

  /**
   * Get all conversations for the current user.
   * 
   * Returns:
   *   Promise<ConversationPreview[]>: List of user conversations with previews
   */
  async getUserConversations(): Promise<ConversationPreview[]> {
    try {
      const response = await ApiClient.get('/conversations/conversations');
      return response.conversations || [];
    } catch (error: any) {
      console.error('[ChatService] Failed to get user conversations:', error);
      throw new Error(error.message || 'Failed to get conversations');
    }
  }

  /**
   * Start a new conversation.
   * 
   * Returns:
   *   Promise<{ conversation_id: string }>: New conversation details
   */
  async startNewConversation(): Promise<{ conversation_id: string }> {
    try {
      const response = await ApiClient.post('/conversations/start', {});
      return response;
    } catch (error: any) {
      console.error('[ChatService] Failed to start new conversation:', error);
      throw new Error(error.message || 'Failed to start new conversation');
    }
  }

  /**
   * Check if the user is authenticated for chat access.
   * 
   * Returns:
   *   Promise<boolean>: True if authenticated, false otherwise
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      return await AuthService.isAuthenticated();
    } catch (error) {
      console.error('[ChatService] Authentication check failed:', error);
      return false;
    }
  }

  /**
   * Format a timestamp for display in chat messages.
   * 
   * Args:
   *   timestamp: ISO timestamp string
   * 
   * Returns:
   *   string: Formatted time string
   */
  formatMessageTime(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      
      // Check if date is invalid
      if (isNaN(date.getTime())) {
        return 'Unknown time';
      }
      
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffMins < 1) {
        return 'Just now';
      } else if (diffMins < 60) {
        return `${diffMins} min ago`;
      } else if (diffHours < 24) {
        return `${diffHours}h ago`;
      } else if (diffDays < 7) {
        return `${diffDays}d ago`;
      } else {
        // For US locale format: MM/DD/YYYY
        return date.toLocaleDateString('en-US');
      }
    } catch (error) {
      console.error('[ChatService] Failed to format timestamp:', error);
      return 'Unknown time';
    }
  }

  /**
   * Check if a message indicates a crisis situation.
   * 
   * Args:
   *   response: Chat response from the API
   * 
   * Returns:
   *   boolean: True if crisis detected, false otherwise
   */
  isCrisisDetected(response: ChatResponse): boolean {
    const crisisLevel = response.response?.crisis_level;
    if (!crisisLevel) {
      return false;
    }
    return ['HIGH', 'CRITICAL'].includes(crisisLevel.toUpperCase());
  }

  /**
   * Get crisis support message for UI display.
   * 
   * Args:
   *   response: Chat response with crisis information
   * 
   * Returns:
   *   string: Crisis support message
   */
  getCrisisSupportMessage(response: ChatResponse): string {
    const crisisLevel = response.response?.crisis_level?.toUpperCase();
    
    if (!crisisLevel || crisisLevel === 'NONE' || crisisLevel === 'LOW') {
      return '';
    }
    
    if (crisisLevel === 'CRITICAL') {
      return 'I notice you might be in crisis. Please consider reaching out for immediate support.';
    } else if (crisisLevel === 'HIGH') {
      return 'I want to make sure you\'re safe. Let\'s talk about getting you some support.';
    } else if (crisisLevel === 'MEDIUM') {
      return 'I\'m here to support you through this difficult time.';
    }
    
    // Fallback for any other crisis levels
    return 'I\'m here to support you through this difficult time.';
  }
}

export default ChatService; 
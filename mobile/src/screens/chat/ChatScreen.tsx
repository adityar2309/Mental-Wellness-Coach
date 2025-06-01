/**
 * Mental Wellness Coach - Chat Screen
 * 
 * Main chat interface for conversations with the AI wellness coach.
 * Features real-time messaging, crisis detection, and conversation history.
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import ChatService, { ChatMessage, ChatResponse } from '../../services/ChatService';
import MessageBubble from '../../components/chat/MessageBubble';
import TypingIndicator from '../../components/chat/TypingIndicator';

export default function ChatScreen() {
  const navigation = useNavigation();
  const chatService = useRef(new ChatService()).current;
  const flatListRef = useRef<FlatList>(null);

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  useEffect(() => {
    initializeChat();
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages, isTyping]);

  /**
   * Initialize chat session.
   */
  const initializeChat = async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);

      // Check authentication
      const isAuthenticated = await chatService.isAuthenticated();
      if (!isAuthenticated) {
        setError('Please log in to start chatting');
        return;
      }

      // Start with a welcome message
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        role: 'assistant',
        content: "Hi! I'm your AI wellness coach. I'm here to support you through any challenges you might be facing. How are you feeling today?",
        timestamp: new Date().toISOString(),
      };

      setMessages([welcomeMessage]);
      setIsLoading(false);
    } catch (error: any) {
      console.error('[ChatScreen] Failed to initialize chat:', error);
      setError('Failed to initialize chat. Please try again.');
      setIsLoading(false);
    }
  };

  /**
   * Send a message to the AI.
   */
  const sendMessage = async (): Promise<void> => {
    if (!inputText.trim() || isTyping) return;

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    setError(null);

    try {
      // Send message to API
      const response = await chatService.sendMessage({
        message: userMessage.content,
        conversation_id: conversationId || undefined,
      });

      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Create AI response message
      const aiMessage: ChatMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.response.text,
        timestamp: new Date().toISOString(),
      };

      // Add AI response
      setMessages(prev => [...prev, aiMessage]);
      setLastResponse(response);

      // Check for crisis detection
      if (chatService.isCrisisDetected(response)) {
        showCrisisAlert(response);
      }

    } catch (error: any) {
      console.error('[ChatScreen] Failed to send message:', error);
      setError('Failed to send message. Please try again.');
      
      // Show error message as AI response
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: "I'm sorry, I'm having trouble responding right now. Please try again in a moment.",
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  /**
   * Show crisis alert to user.
   */
  const showCrisisAlert = (response: ChatResponse): void => {
    const crisisMessage = chatService.getCrisisSupportMessage(response);
    const crisisLevel = response.response.crisis_level;

    Alert.alert(
      'Support Available',
      crisisMessage,
      [
        { text: 'Continue Talking', style: 'default' },
        { 
          text: 'Get Help Resources', 
          style: 'default',
          onPress: () => showCrisisResources(response)
        },
      ],
    );
  };

  /**
   * Show crisis resources to user.
   */
  const showCrisisResources = (response: ChatResponse): void => {
    const resources = response.response.safety_resources || [];
    const actions = response.response.suggested_actions || [];
    
    let resourceText = 'Available Support:\n\n';
    
    if (actions.length > 0) {
      resourceText += 'Suggested Actions:\n';
      actions.forEach((action, index) => {
        resourceText += `• ${action}\n`;
      });
      resourceText += '\n';
    }

    resourceText += 'Crisis Hotlines:\n';
    resourceText += '• National Suicide Prevention Lifeline: 988\n';
    resourceText += '• Crisis Text Line: Text HOME to 741741\n';
    resourceText += '• Emergency Services: 911\n';

    Alert.alert(
      'Crisis Support Resources',
      resourceText,
      [{ text: 'Close', style: 'default' }],
    );
  };

  /**
   * Render individual message item.
   */
  const renderMessage = ({ item }: { item: ChatMessage }) => {
    const showCrisis = lastResponse && 
                      item.role === 'assistant' && 
                      item.id === lastResponse.message_id &&
                      chatService.isCrisisDetected(lastResponse);

    const crisisLevel = showCrisis ? lastResponse?.response.crisis_level : undefined;

    return (
      <MessageBubble
        message={item}
        showCrisis={showCrisis}
        crisisLevel={crisisLevel}
      />
    );
  };

  /**
   * Render chat input area.
   */
  const renderInputArea = () => (
    <View style={styles.inputContainer}>
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
      
      <View style={styles.inputRow}>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Type your message..."
          placeholderTextColor="#9ca3af"
          multiline
          maxLength={1000}
          editable={!isTyping}
          onSubmitEditing={sendMessage}
          returnKeyType="send"
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            (!inputText.trim() || isTyping) && styles.sendButtonDisabled,
          ]}
          onPress={sendMessage}
          disabled={!inputText.trim() || isTyping}
        >
          {isTyping ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6366f1" testID="activity-indicator" />
          <Text style={styles.loadingText}>Starting chat...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>AI Wellness Coach</Text>
          <Text style={styles.headerSubtitle}>
            {isTyping ? 'Thinking...' : 'Here to help'}
          </Text>
        </View>

        {/* Messages List */}
        <FlatList
          ref={flatListRef}
          style={styles.messagesList}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderMessage}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() => 
            flatListRef.current?.scrollToEnd({ animated: true })
          }
          ListFooterComponent={() => (
            <TypingIndicator visible={isTyping} />
          )}
        />

        {/* Input Area */}
        {renderInputArea()}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
    fontFamily: 'Inter-Regular',
  },
  header: {
    backgroundColor: '#ffffff',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    fontFamily: 'Inter-SemiBold',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
    fontFamily: 'Inter-Regular',
  },
  messagesList: {
    flex: 1,
    paddingVertical: 16,
  },
  inputContainer: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  errorContainer: {
    backgroundColor: '#fef2f2',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  errorText: {
    fontSize: 14,
    color: '#dc2626',
    fontFamily: 'Inter-Regular',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    maxHeight: 100,
    marginRight: 12,
    fontFamily: 'Inter-Regular',
    backgroundColor: '#ffffff',
  },
  sendButton: {
    backgroundColor: '#6366f1',
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 12,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 60,
  },
  sendButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  sendButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'Inter-SemiBold',
  },
}); 
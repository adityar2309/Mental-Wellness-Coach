/**
 * Mental Wellness Coach - Message Bubble Component
 * 
 * Displays individual chat messages with appropriate styling
 * for user and AI messages, including crisis detection indicators.
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
} from 'react-native';
import { ChatMessage } from '../../services/ChatService';

interface MessageBubbleProps {
  message: ChatMessage;
  isTyping?: boolean;
  showCrisis?: boolean;
  crisisLevel?: string;
  onPress?: () => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isTyping = false,
  showCrisis = false,
  crisisLevel,
  onPress,
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  // Format timestamp for display
  const formatTime = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      return '';
    }
  };

  // Get crisis indicator styles
  const getCrisisStyles = () => {
    if (!showCrisis || !crisisLevel) return {};
    
    switch (crisisLevel.toUpperCase()) {
      case 'CRITICAL':
        return {
          borderLeftWidth: 4,
          borderLeftColor: '#dc2626', // red-600
        };
      case 'HIGH':
        return {
          borderLeftWidth: 4,
          borderLeftColor: '#ea580c', // orange-600
        };
      case 'MEDIUM':
        return {
          borderLeftWidth: 4,
          borderLeftColor: '#d97706', // amber-600
        };
      default:
        return {};
    }
  };

  return (
    <View
      style={[
        styles.container,
        isUser ? styles.userContainer : styles.assistantContainer,
      ]}
    >
      <View
        style={[
          styles.bubble,
          isUser ? styles.userBubble : styles.assistantBubble,
          getCrisisStyles(),
          showCrisis && styles.crisisBubble,
        ]}
        accessible={true}
        accessibilityLabel={`${isUser ? 'Your message' : 'AI response'}: ${message.content}`}
        accessibilityRole="text"
      >
        {showCrisis && crisisLevel && (
          <View style={styles.crisisIndicator}>
            <Text style={styles.crisisText}>
              Crisis Level: {crisisLevel}
            </Text>
          </View>
        )}
        
        <Text
          style={[
            styles.messageText,
            isUser ? styles.userText : styles.assistantText,
          ]}
        >
          {message.content}
        </Text>
        
        {message.timestamp && (
          <Text
            style={[
              styles.timestamp,
              isUser ? styles.userTimestamp : styles.assistantTimestamp,
            ]}
          >
            {formatTime(message.timestamp)}
          </Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 4,
    marginHorizontal: 16,
  },
  userContainer: {
    alignItems: 'flex-end',
  },
  assistantContainer: {
    alignItems: 'flex-start',
  },
  bubble: {
    maxWidth: '80%',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 18,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  userBubble: {
    backgroundColor: '#6366f1', // indigo-500
    borderBottomRightRadius: 6,
  },
  assistantBubble: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e5e7eb', // gray-200
    borderBottomLeftRadius: 6,
  },
  crisisBubble: {
    borderWidth: 2,
    borderColor: '#dc2626', // red-600
  },
  crisisIndicator: {
    backgroundColor: '#fef2f2', // red-50
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginBottom: 8,
  },
  crisisText: {
    fontSize: 12,
    color: '#dc2626', // red-600
    fontWeight: '600',
    fontFamily: 'Inter-SemiBold',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
    fontFamily: 'Inter-Regular',
  },
  userText: {
    color: '#ffffff',
  },
  assistantText: {
    color: '#1f2937', // gray-800
  },
  timestamp: {
    fontSize: 12,
    marginTop: 4,
    fontFamily: 'Inter-Regular',
  },
  userTimestamp: {
    color: '#c7d2fe', // indigo-200
    textAlign: 'right',
  },
  assistantTimestamp: {
    color: '#9ca3af', // gray-400
    textAlign: 'left',
  },
});

export default MessageBubble; 
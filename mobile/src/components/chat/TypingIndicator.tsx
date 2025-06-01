/**
 * Mental Wellness Coach - Typing Indicator Component
 * 
 * Animated typing indicator to show when the AI is processing a response.
 */

import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
} from 'react-native';

interface TypingIndicatorProps {
  visible: boolean;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ visible }) => {
  const dot1Opacity = useRef(new Animated.Value(0.3)).current;
  const dot2Opacity = useRef(new Animated.Value(0.3)).current;
  const dot3Opacity = useRef(new Animated.Value(0.3)).current;
  const containerOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      // Show the container
      Animated.timing(containerOpacity, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }).start();

      // Animate the dots
      const animateDots = () => {
        const animateDot = (dotOpacity: Animated.Value, delay: number) => {
          return Animated.sequence([
            Animated.delay(delay),
            Animated.timing(dotOpacity, {
              toValue: 1,
              duration: 500,
              useNativeDriver: true,
            }),
            Animated.timing(dotOpacity, {
              toValue: 0.3,
              duration: 500,
              useNativeDriver: true,
            }),
          ]);
        };

        Animated.loop(
          Animated.parallel([
            animateDot(dot1Opacity, 0),
            animateDot(dot2Opacity, 200),
            animateDot(dot3Opacity, 400),
          ])
        ).start();
      };

      animateDots();
    } else {
      // Hide the container
      Animated.timing(containerOpacity, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  }, [visible, containerOpacity, dot1Opacity, dot2Opacity, dot3Opacity]);

  if (!visible) {
    return null;
  }

  return (
    <Animated.View
      style={[
        styles.container,
        { opacity: containerOpacity }
      ]}
    >
      <View style={styles.bubble}>
        <View style={styles.dotContainer}>
          <Animated.View
            style={[
              styles.dot,
              { opacity: dot1Opacity }
            ]}
          />
          <Animated.View
            style={[
              styles.dot,
              { opacity: dot2Opacity }
            ]}
          />
          <Animated.View
            style={[
              styles.dot,
              { opacity: dot3Opacity }
            ]}
          />
        </View>
        <Text style={styles.typingText}>AI is typing...</Text>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 4,
    marginHorizontal: 16,
    alignItems: 'flex-start',
  },
  bubble: {
    backgroundColor: '#f3f4f6', // gray-100
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 18,
    borderBottomLeftRadius: 6,
    borderWidth: 1,
    borderColor: '#e5e7eb', // gray-200
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    minHeight: 50,
    justifyContent: 'center',
  },
  dotContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#6366f1', // indigo-500
    marginHorizontal: 2,
  },
  typingText: {
    fontSize: 12,
    color: '#6b7280', // gray-500
    textAlign: 'center',
    fontFamily: 'Inter-Regular',
    fontStyle: 'italic',
  },
});

export default TypingIndicator; 
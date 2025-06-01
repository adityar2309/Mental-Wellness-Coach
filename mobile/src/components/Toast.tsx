import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Animated, Dimensions } from 'react-native';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  duration?: number;
  onHide?: () => void;
}

export const Toast: React.FC<ToastProps> = ({ 
  message, 
  type = 'success', 
  duration = 3000, 
  onHide 
}) => {
  const [fadeAnim] = useState(new Animated.Value(0));

  useEffect(() => {
    // Fade in
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();

    // Auto hide after duration
    const timer = setTimeout(() => {
      // Fade out
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }).start(() => {
        onHide?.();
      });
    }, duration);

    return () => clearTimeout(timer);
  }, [fadeAnim, duration, onHide]);

  const getBackgroundColor = () => {
    switch (type) {
      case 'success':
        return '#10b981';
      case 'error':
        return '#ef4444';
      case 'info':
        return '#3b82f6';
      default:
        return '#10b981';
    }
  };

  return (
    <Animated.View
      style={[
        styles.container,
        { 
          backgroundColor: getBackgroundColor(),
          opacity: fadeAnim,
          transform: [{
            translateY: fadeAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [-50, 0],
            }),
          }],
        },
      ]}
    >
      <Text style={styles.message}>{message}</Text>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 60,
    left: 20,
    right: 20,
    zIndex: 9999,
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  message: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    fontFamily: 'Inter-Medium',
  },
});

// Toast manager for global usage
let toastRef: React.RefObject<any> | null = null;

export const showToast = (message: string, type?: 'success' | 'error' | 'info') => {
  // This would typically be managed by a global state manager or context
  console.log(`🍞 Toast: ${message} (${type})`);
}; 
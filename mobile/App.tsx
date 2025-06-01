import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import * as SplashScreen from 'expo-splash-screen';
import * as Font from 'expo-font';

// Screens
import OnboardingScreen from './src/screens/OnboardingScreen';
import LoginScreen from './src/screens/auth/LoginScreen';
import RegisterScreen from './src/screens/auth/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import MoodCheckInScreen from './src/screens/mood/MoodCheckInScreen';
import ChatScreen from './src/screens/chat/ChatScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import JournalScreen from './src/screens/journal/JournalScreen';
import JournalEntryScreen from './src/screens/journal/JournalEntryScreen';
import JournalAnalyticsScreen from './src/screens/journal/JournalAnalyticsScreen';
import MindfulnessScreen from './src/screens/mindfulness/MindfulnessScreen';
import BreathingExerciseScreen from './src/screens/mindfulness/BreathingExerciseScreen';

// Services
import { AuthService } from './src/services/AuthService';

// Types
export type RootStackParamList = {
  Onboarding: undefined;
  Login: undefined;
  Register: undefined;
  Home: undefined;
  MoodCheckIn: undefined;
  Chat: undefined;
  Profile: undefined;
  Journal: undefined;
  JournalEntry: { entryId?: number; isEditing: boolean };
  JournalAnalytics: undefined;
  Mindfulness: undefined;
  BreathingExercise: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

// Prevent the splash screen from auto-hiding
SplashScreen.preventAutoHideAsync();

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isFirstLaunch, setIsFirstLaunch] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    loadApp();
  }, []);

  const loadApp = async () => {
    try {
      // Load fonts
      await Font.loadAsync({
        'Inter-Regular': require('./src/assets/fonts/Inter-Regular.ttf'),
        'Inter-Medium': require('./src/assets/fonts/Inter-Medium.ttf'),
        'Inter-SemiBold': require('./src/assets/fonts/Inter-SemiBold.ttf'),
      });

      // Check if user has completed onboarding
      const hasCompletedOnboarding = await AuthService.hasCompletedOnboarding();
      setIsFirstLaunch(!hasCompletedOnboarding);

      // Check authentication status
      const authStatus = await AuthService.isAuthenticated();
      setIsAuthenticated(authStatus);

    } catch (error) {
      console.warn('Error loading app:', error);
    } finally {
      setIsLoading(false);
      await SplashScreen.hideAsync();
    }
  };

  const refreshAuthState = async () => {
    try {
      const authStatus = await AuthService.isAuthenticated();
      setIsAuthenticated(authStatus);
    } catch (error) {
      console.warn('Error refreshing auth state:', error);
    }
  };

  const getInitialRouteName = (): keyof RootStackParamList => {
    if (isFirstLaunch) return 'Onboarding';
    if (!isAuthenticated) return 'Login';
    return 'Home';
  };

  if (isLoading) {
    return null; // Splash screen is shown
  }

  return (
    <NavigationContainer
      onStateChange={refreshAuthState}
    >
      <StatusBar style="auto" />
      <Stack.Navigator
        initialRouteName={getInitialRouteName()}
        screenOptions={{
          headerStyle: {
            backgroundColor: '#6366f1',
          },
          headerTintColor: '#ffffff',
          headerTitleStyle: {
            fontFamily: 'Inter-SemiBold',
            fontSize: 18,
          },
        }}
      >
        {/* Onboarding Flow */}
        <Stack.Screen 
          name="Onboarding" 
          component={OnboardingScreen}
          options={{ headerShown: false }}
        />

        {/* Authentication Screens */}
        <Stack.Screen 
          name="Login" 
          component={LoginScreen}
          options={{ 
            title: 'Welcome Back',
            headerShown: false 
          }}
        />
        <Stack.Screen 
          name="Register" 
          component={RegisterScreen}
          options={{ 
            title: 'Create Account',
            headerBackTitleVisible: false
          }}
        />

        {/* Main App Screens */}
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ 
            title: 'Mental Wellness Coach',
            headerLeft: () => null, // Disable back button
          }}
        />
        <Stack.Screen 
          name="MoodCheckIn" 
          component={MoodCheckInScreen}
          options={{ title: 'How are you feeling?' }}
        />
        <Stack.Screen 
          name="Chat" 
          component={ChatScreen}
          options={{ title: 'Chat with AI Coach' }}
        />
        <Stack.Screen 
          name="Profile" 
          component={ProfileScreen}
          options={{ title: 'Your Profile' }}
        />
        <Stack.Screen 
          name="Journal" 
          component={JournalScreen}
          options={{ title: 'Your Journal' }}
        />
        <Stack.Screen 
          name="JournalEntry" 
          component={JournalEntryScreen}
          options={{ 
            title: 'Journal Entry',
            headerBackTitleVisible: false 
          }}
        />
        <Stack.Screen 
          name="JournalAnalytics" 
          component={JournalAnalyticsScreen}
          options={{ 
            title: 'Analytics',
            headerBackTitleVisible: false 
          }}
        />
        <Stack.Screen 
          name="Mindfulness" 
          component={MindfulnessScreen}
          options={{ title: 'Mindfulness' }}
        />
        <Stack.Screen 
          name="BreathingExercise" 
          component={BreathingExerciseScreen}
          options={{ title: 'Breathing Exercise' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
} 
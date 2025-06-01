import React, { useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../../App';
import { AuthService } from '../services/AuthService';

type OnboardingScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'Onboarding'
>;

interface Props {
  navigation: OnboardingScreenNavigationProp;
}

const { width, height } = Dimensions.get('window');

interface OnboardingStep {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  emoji: string;
  color: string;
}

const onboardingSteps: OnboardingStep[] = [
  {
    id: 1,
    title: 'Welcome to Your Mental Wellness Journey',
    subtitle: 'AI-Powered Support',
    description: 'Meet your personal AI wellness coach. Get 24/7 support, guidance, and evidence-based techniques to improve your mental health.',
    emoji: '🤗',
    color: '#6366f1',
  },
  {
    id: 2,
    title: 'Track Your Mood Daily',
    subtitle: 'Understand Your Patterns',
    description: 'Log your daily mood, energy levels, and emotions. Discover patterns and triggers to better understand your mental wellness.',
    emoji: '📊',
    color: '#8b5cf6',
  },
  {
    id: 3,
    title: 'AI Conversations & Support',
    subtitle: 'Always Here to Listen',
    description: 'Chat with our empathetic AI coach anytime. Share your thoughts, get coping strategies, and receive personalized mental health support.',
    emoji: '💬',
    color: '#06b6d4',
  },
  {
    id: 4,
    title: 'Crisis Detection & Safety',
    subtitle: 'Your Safety is Our Priority',
    description: 'Advanced AI monitors for crisis indicators and provides immediate resources, emergency contacts, and professional support when needed.',
    emoji: '🆘',
    color: '#ef4444',
  },
  {
    id: 5,
    title: 'Privacy & Security First',
    subtitle: 'Your Data is Protected',
    description: 'End-to-end encryption ensures your mental health data stays private. HIPAA-compliant security with full control over your information.',
    emoji: '🔒',
    color: '#10b981',
  },
];

export default function OnboardingScreen({ navigation }: Props) {
  const [currentStep, setCurrentStep] = useState(0);
  const scrollViewRef = useRef<ScrollView>(null);

  const handleNext = () => {
    if (currentStep < onboardingSteps.length - 1) {
      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);
      scrollViewRef.current?.scrollTo({ x: nextStep * width, animated: true });
    } else {
      handleGetStarted();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      const prevStep = currentStep - 1;
      setCurrentStep(prevStep);
      scrollViewRef.current?.scrollTo({ x: prevStep * width, animated: true });
    }
  };

  const handleGetStarted = async () => {
    await AuthService.markOnboardingCompleted();
    navigation.replace('Login');
  };

  const handleSkip = async () => {
    await AuthService.markOnboardingCompleted();
    navigation.replace('Login');
  };

  const renderStep = (step: OnboardingStep, index: number) => (
    <View key={step.id} style={[styles.stepContainer, { backgroundColor: step.color }]}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.content}>
          <View style={styles.emojiContainer}>
            <Text style={styles.emoji}>{step.emoji}</Text>
          </View>
          
          <View style={styles.textContainer}>
            <Text style={styles.title}>{step.title}</Text>
            <Text style={styles.subtitle}>{step.subtitle}</Text>
            <Text style={styles.description}>{step.description}</Text>
          </View>

          <View style={styles.pagination}>
            {onboardingSteps.map((_, i) => (
              <View
                key={i}
                style={[
                  styles.paginationDot,
                  {
                    backgroundColor: i === currentStep ? '#ffffff' : 'rgba(255, 255, 255, 0.5)',
                  },
                ]}
              />
            ))}
          </View>

          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={styles.skipButton}
              onPress={handleSkip}
            >
              <Text style={styles.skipButtonText}>Skip</Text>
            </TouchableOpacity>

            <View style={styles.navigationButtons}>
              {currentStep > 0 && (
                <TouchableOpacity
                  style={styles.previousButton}
                  onPress={handlePrevious}
                >
                  <Text style={styles.previousButtonText}>Previous</Text>
                </TouchableOpacity>
              )}

              <TouchableOpacity
                style={styles.nextButton}
                onPress={handleNext}
              >
                <Text style={styles.nextButtonText}>
                  {currentStep === onboardingSteps.length - 1 ? 'Get Started' : 'Next'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </SafeAreaView>
    </View>
  );

  return (
    <View style={styles.container}>
      <ScrollView
        ref={scrollViewRef}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        scrollEnabled={false}
        style={styles.scrollView}
      >
        {onboardingSteps.map((step, index) => renderStep(step, index))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  stepContainer: {
    width,
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'space-between',
    paddingHorizontal: 32,
    paddingVertical: 48,
  },
  emojiContainer: {
    alignItems: 'center',
    marginTop: 60,
  },
  emoji: {
    fontSize: 120,
    textAlign: 'center',
  },
  textContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 12,
    fontFamily: 'Inter-SemiBold',
  },
  subtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    marginBottom: 24,
    fontFamily: 'Inter-Medium',
  },
  description: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    lineHeight: 24,
    fontFamily: 'Inter-Regular',
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 32,
  },
  paginationDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginHorizontal: 6,
  },
  buttonContainer: {
    gap: 16,
  },
  skipButton: {
    alignSelf: 'center',
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  skipButtonText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 16,
    fontFamily: 'Inter-Medium',
  },
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  previousButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 25,
    flex: 1,
    marginRight: 12,
  },
  previousButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    fontFamily: 'Inter-Medium',
  },
  nextButton: {
    backgroundColor: '#ffffff',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 25,
    flex: 1,
    marginLeft: 12,
  },
  nextButtonText: {
    color: '#1f2937',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    fontFamily: 'Inter-Medium',
  },
}); 
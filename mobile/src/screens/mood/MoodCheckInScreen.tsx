import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../../../App';
import { MoodApi } from '../../services/ApiClient';

type MoodCheckInScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'MoodCheckIn'
>;

interface Props {
  navigation: MoodCheckInScreenNavigationProp;
}

export default function MoodCheckInScreen({ navigation }: Props) {
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const moodOptions = [
    { value: 1, emoji: '😰', label: 'Very Bad' },
    { value: 2, emoji: '😞', label: 'Bad' },
    { value: 3, emoji: '😐', label: 'Okay' },
    { value: 4, emoji: '🙂', label: 'Good' },
    { value: 5, emoji: '😊', label: 'Great' },
  ];

  const handleSubmit = async () => {
    if (!selectedMood) {
      Alert.alert('Please select your mood', 'Choose how you\'re feeling today.');
      return;
    }

    setIsLoading(true);
    try {
      await MoodApi.quickCheckIn(selectedMood);
      Alert.alert(
        'Mood Recorded!',
        'Thank you for checking in. Your mood has been saved.',
        [
          { text: 'OK', onPress: () => navigation.goBack() }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to save your mood. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>How are you feeling today?</Text>
        <Text style={styles.subtitle}>Select your current mood</Text>

        <View style={styles.moodGrid}>
          {moodOptions.map((mood) => (
            <TouchableOpacity
              key={mood.value}
              style={[
                styles.moodCard,
                selectedMood === mood.value && styles.moodCardSelected,
              ]}
              onPress={() => setSelectedMood(mood.value)}
            >
              <Text style={styles.moodEmoji}>{mood.emoji}</Text>
              <Text style={styles.moodLabel}>{mood.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          style={[
            styles.submitButton,
            (!selectedMood || isLoading) && styles.submitButtonDisabled,
          ]}
          onPress={handleSubmit}
          disabled={!selectedMood || isLoading}
        >
          <Text style={styles.submitButtonText}>
            {isLoading ? 'Saving...' : 'Save Mood'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 8,
    fontFamily: 'Inter-SemiBold',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 48,
    fontFamily: 'Inter-Regular',
  },
  moodGrid: {
    gap: 16,
    marginBottom: 48,
  },
  moodCard: {
    backgroundColor: '#ffffff',
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  moodCardSelected: {
    borderColor: '#6366f1',
    backgroundColor: '#f0f9ff',
  },
  moodEmoji: {
    fontSize: 48,
    marginBottom: 12,
  },
  moodLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    fontFamily: 'Inter-Medium',
  },
  submitButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 18,
    borderRadius: 12,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    fontFamily: 'Inter-Medium',
  },
}); 
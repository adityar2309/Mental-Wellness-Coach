import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Alert,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../../App';
import { AuthService, User } from '../services/AuthService';

type HomeScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'Home'
>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

export default function HomeScreen({ navigation }: Props) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await AuthService.getUserData();
      setUser(userData);
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: async () => {
            await AuthService.logout();
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.greeting}>
            {getGreeting()}, {user?.username || 'there'}! 👋
          </Text>
          <Text style={styles.subtitle}>How are you feeling today?</Text>
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: '#6366f1' }]}
            onPress={() => navigation.navigate('MoodCheckIn')}
          >
            <Text style={styles.actionEmoji}>😊</Text>
            <Text style={styles.actionTitle}>Mood Check-In</Text>
            <Text style={styles.actionSubtitle}>How are you feeling?</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: '#06b6d4' }]}
            onPress={() => navigation.navigate('Chat')}
          >
            <Text style={styles.actionEmoji}>💬</Text>
            <Text style={styles.actionTitle}>Chat with AI</Text>
            <Text style={styles.actionSubtitle}>Get support & guidance</Text>
          </TouchableOpacity>
        </View>

        {/* Features Grid */}
        <View style={styles.featuresGrid}>
          <TouchableOpacity style={styles.featureCard}>
            <Text style={styles.featureEmoji}>📊</Text>
            <Text style={styles.featureTitle}>Analytics</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => navigation.navigate('Journal')}
          >
            <Text style={styles.featureEmoji}>📝</Text>
            <Text style={styles.featureTitle}>Journal</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.featureCard}>
            <Text style={styles.featureEmoji}>🧘</Text>
            <Text style={styles.featureTitle}>Mindfulness</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.featureCard}>
            <Text style={styles.featureEmoji}>🆘</Text>
            <Text style={styles.featureTitle}>Crisis Help</Text>
          </TouchableOpacity>
        </View>

        {/* Profile Section */}
        <View style={styles.profileSection}>
          <TouchableOpacity
            style={styles.profileButton}
            onPress={() => navigation.navigate('Profile')}
          >
            <Text style={styles.profileText}>View Profile</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.logoutButton}
            onPress={handleLogout}
          >
            <Text style={styles.logoutText}>Sign Out</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 24,
  },
  header: {
    marginBottom: 32,
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
    fontFamily: 'Inter-SemiBold',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    fontFamily: 'Inter-Regular',
  },
  quickActions: {
    gap: 16,
    marginBottom: 32,
  },
  actionCard: {
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
  },
  actionEmoji: {
    fontSize: 48,
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
    fontFamily: 'Inter-SemiBold',
  },
  actionSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    fontFamily: 'Inter-Regular',
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
    marginBottom: 32,
  },
  featureCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
    minWidth: '45%',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  featureEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  featureTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    fontFamily: 'Inter-Medium',
  },
  profileSection: {
    gap: 12,
  },
  profileButton: {
    backgroundColor: '#ffffff',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d1d5db',
  },
  profileText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    fontFamily: 'Inter-Medium',
  },
  logoutButton: {
    backgroundColor: '#ef4444',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    fontFamily: 'Inter-Medium',
  },
}); 
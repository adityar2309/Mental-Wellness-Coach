import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import {
  MindfulnessService,
  SessionTemplate,
  MindfulnessSession,
  MindfulnessAnalytics,
} from '../../services/MindfulnessService';

interface MindfulnessScreenProps {
  navigation: any;
}

const MindfulnessScreen: React.FC<MindfulnessScreenProps> = ({ navigation }) => {
  const [templates, setTemplates] = useState<SessionTemplate[]>([]);
  const [recentSessions, setRecentSessions] = useState<MindfulnessSession[]>([]);
  const [analytics, setAnalytics] = useState<MindfulnessAnalytics | null>(null);
  const [recommendations, setRecommendations] = useState<SessionTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [templatesResponse, recent, analyticsResponse, personalizedRecs] = await Promise.all([
        MindfulnessService.getTemplates(),
        MindfulnessService.getRecentSessions(),
        MindfulnessService.getAnalytics(30),
        MindfulnessService.getPersonalizedRecommendations(),
      ]);

      // Flatten templates into a single array for quick start options
      const allTemplates = [
        ...templatesResponse.templates.breathing,
        ...templatesResponse.templates.meditation,
        ...templatesResponse.templates.body_scan,
        ...templatesResponse.templates.progressive_relaxation,
      ];

      setTemplates(allTemplates);
      setRecentSessions(recent);
      setAnalytics(analyticsResponse.analytics);
      setRecommendations(personalizedRecs);
    } catch (error) {
      console.error('Error loading mindfulness data:', error);
      Alert.alert('Error', 'Failed to load mindfulness data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleStartSession = (template: SessionTemplate, sessionType: string) => {
    navigation.navigate('SessionSetup', { template, sessionType });
  };

  const handleViewAllSessions = () => {
    navigation.navigate('SessionHistory');
  };

  const handleViewAnalytics = () => {
    navigation.navigate('MindfulnessAnalytics', { analytics });
  };

  const getSessionTypeColor = (type: string) => {
    switch (type) {
      case 'breathing': return '#4ECDC4';
      case 'meditation': return '#45B7D1';
      case 'body_scan': return '#F7DC6F';
      case 'progressive_relaxation': return '#BB8FCE';
      default: return '#95A5A6';
    }
  };

  const SessionCard: React.FC<{ template: SessionTemplate; sessionType: string }> = ({ template, sessionType }) => (
    <TouchableOpacity
      style={[styles.sessionCard, { borderLeftColor: getSessionTypeColor(sessionType) }]}
      onPress={() => handleStartSession(template, sessionType)}
    >
      <View style={styles.sessionCardHeader}>
        <Text style={styles.sessionTitle}>{template.title}</Text>
        <Text style={styles.sessionDuration}>{template.duration_minutes} min</Text>
      </View>
      <Text style={styles.sessionDescription} numberOfLines={2}>
        {template.description}
      </Text>
      <View style={styles.sessionTypeContainer}>
        <Text style={[styles.sessionType, { backgroundColor: getSessionTypeColor(sessionType) }]}>
          {sessionType.replace('_', ' ').toUpperCase()}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const RecentSessionCard: React.FC<{ session: MindfulnessSession }> = ({ session }) => (
    <TouchableOpacity style={styles.recentSessionCard}>
      <View style={styles.recentSessionHeader}>
        <Text style={styles.recentSessionTitle}>{session.title}</Text>
        <Text style={styles.recentSessionDate}>
          {new Date(session.created_at).toLocaleDateString()}
        </Text>
      </View>
      <View style={styles.recentSessionDetails}>
        <Text style={styles.recentSessionDuration}>
          {session.completed_duration_minutes || session.duration_minutes} min
        </Text>
        {session.effectiveness_rating && (
          <Text style={styles.recentSessionRating}>
            ⭐ {session.effectiveness_rating}/10
          </Text>
        )}
        <View style={[styles.statusBadge, { 
          backgroundColor: session.completed ? '#27AE60' : '#F39C12' 
        }]}>
          <Text style={styles.statusText}>
            {session.completed ? 'Completed' : 'In Progress'}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading mindfulness content...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mindfulness</Text>
        <Text style={styles.headerSubtitle}>Find your inner peace</Text>
      </View>

      {/* Analytics Summary */}
      {analytics && (
        <TouchableOpacity style={styles.analyticsCard} onPress={handleViewAnalytics}>
          <Text style={styles.analyticsTitle}>Your Progress</Text>
          <View style={styles.analyticsRow}>
            <View style={styles.analyticsStat}>
              <Text style={styles.analyticsNumber}>{analytics.streak_days}</Text>
              <Text style={styles.analyticsLabel}>Day Streak</Text>
            </View>
            <View style={styles.analyticsStat}>
              <Text style={styles.analyticsNumber}>{analytics.total_minutes}</Text>
              <Text style={styles.analyticsLabel}>Total Minutes</Text>
            </View>
            <View style={styles.analyticsStat}>
              <Text style={styles.analyticsNumber}>{analytics.completed_sessions}</Text>
              <Text style={styles.analyticsLabel}>Sessions</Text>
            </View>
          </View>
        </TouchableOpacity>
      )}

      {/* Recommended for You */}
      {recommendations.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recommended for You</Text>
          {recommendations.map((template, index) => (
            <SessionCard 
              key={`rec-${index}`} 
              template={template} 
              sessionType={'meditation'} // Default for recommendations
            />
          ))}
        </View>
      )}

      {/* Quick Start Options */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Start</Text>
        <View style={styles.quickStartGrid}>
          <TouchableOpacity 
            style={[styles.quickStartCard, { backgroundColor: '#4ECDC4' }]}
            onPress={() => navigation.navigate('BreathingExercise')}
          >
            <Text style={styles.quickStartEmoji}>🫁</Text>
            <Text style={styles.quickStartTitle}>Breathing</Text>
            <Text style={styles.quickStartSubtitle}>5-10 min</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.quickStartCard, { backgroundColor: '#45B7D1' }]}
            onPress={() => navigation.navigate('MeditationSession')}
          >
            <Text style={styles.quickStartEmoji}>🧘</Text>
            <Text style={styles.quickStartTitle}>Meditation</Text>
            <Text style={styles.quickStartSubtitle}>10-20 min</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.quickStartCard, { backgroundColor: '#F7DC6F' }]}
            onPress={() => navigation.navigate('BodyScanSession')}
          >
            <Text style={styles.quickStartEmoji}>🎯</Text>
            <Text style={styles.quickStartTitle}>Body Scan</Text>
            <Text style={styles.quickStartSubtitle}>15-25 min</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.quickStartCard, { backgroundColor: '#BB8FCE' }]}
            onPress={() => navigation.navigate('RelaxationSession')}
          >
            <Text style={styles.quickStartEmoji}>💆</Text>
            <Text style={styles.quickStartTitle}>Relaxation</Text>
            <Text style={styles.quickStartSubtitle}>10-15 min</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Sessions */}
      {recentSessions.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Sessions</Text>
            <TouchableOpacity onPress={handleViewAllSessions}>
              <Text style={styles.viewAllLink}>View All</Text>
            </TouchableOpacity>
          </View>
          {recentSessions.slice(0, 3).map((session) => (
            <RecentSessionCard key={session.id} session={session} />
          ))}
        </View>
      )}

      {/* Browse All Templates */}
      <View style={styles.section}>
        <TouchableOpacity 
          style={styles.browseAllButton}
          onPress={() => navigation.navigate('SessionTemplates')}
        >
          <Text style={styles.browseAllText}>Browse All Sessions</Text>
          <Text style={styles.browseAllArrow}>→</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    fontSize: 16,
    color: '#7F8C8D',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#ECF0F1',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#7F8C8D',
  },
  analyticsCard: {
    backgroundColor: '#FFFFFF',
    margin: 20,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  analyticsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 15,
  },
  analyticsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  analyticsStat: {
    alignItems: 'center',
  },
  analyticsNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#27AE60',
  },
  analyticsLabel: {
    fontSize: 12,
    color: '#7F8C8D',
    marginTop: 4,
  },
  section: {
    margin: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 15,
  },
  viewAllLink: {
    fontSize: 14,
    color: '#3498DB',
    fontWeight: '500',
  },
  sessionCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  sessionCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sessionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    flex: 1,
  },
  sessionDuration: {
    fontSize: 14,
    color: '#7F8C8D',
    fontWeight: '500',
  },
  sessionDescription: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
    marginBottom: 8,
  },
  sessionTypeContainer: {
    alignItems: 'flex-start',
  },
  sessionType: {
    fontSize: 10,
    color: '#FFFFFF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    fontWeight: '600',
    overflow: 'hidden',
  },
  quickStartGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickStartCard: {
    width: '48%',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  quickStartEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  quickStartTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  quickStartSubtitle: {
    fontSize: 12,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  recentSessionCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  recentSessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recentSessionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    flex: 1,
  },
  recentSessionDate: {
    fontSize: 12,
    color: '#7F8C8D',
  },
  recentSessionDetails: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  recentSessionDuration: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  recentSessionRating: {
    fontSize: 14,
    color: '#F39C12',
    fontWeight: '500',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 10,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  browseAllButton: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  browseAllText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
  },
  browseAllArrow: {
    fontSize: 18,
    color: '#3498DB',
    fontWeight: 'bold',
  },
});

export default MindfulnessScreen; 
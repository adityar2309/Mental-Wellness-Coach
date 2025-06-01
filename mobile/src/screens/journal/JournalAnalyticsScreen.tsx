import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Alert,
  RefreshControl,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useFocusEffect } from '@react-navigation/native';
import { RootStackParamList } from '../../../App';
import { JournalService, JournalAnalytics } from '../../services/JournalService';

type JournalAnalyticsScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'JournalAnalytics'
>;

interface Props {
  navigation: JournalAnalyticsScreenNavigationProp;
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  emoji?: string;
  color?: string;
}

interface TrendCardProps {
  title: string;
  trend: 'improving' | 'declining' | 'stable';
  value?: number;
  subtitle?: string;
}

interface TopItemsCardProps {
  title: string;
  items: Array<{ name: string; count: number }>;
  emoji?: string;
  maxItems?: number;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, emoji, color = '#6366f1' }) => (
  <View style={[styles.statCard, { borderLeftColor: color }]}>
    <View style={styles.statHeader}>
      {emoji && <Text style={styles.statEmoji}>{emoji}</Text>}
      <Text style={styles.statTitle}>{title}</Text>
    </View>
    <Text style={[styles.statValue, { color }]}>{value}</Text>
    {subtitle && <Text style={styles.statSubtitle}>{subtitle}</Text>}
  </View>
);

const TrendCard: React.FC<TrendCardProps> = ({ title, trend, value, subtitle }) => {
  const getTrendInfo = (trend: string) => {
    switch (trend) {
      case 'improving':
        return { emoji: '📈', color: '#10b981', text: 'Improving' };
      case 'declining':
        return { emoji: '📉', color: '#ef4444', text: 'Declining' };
      default:
        return { emoji: '📊', color: '#6b7280', text: 'Stable' };
    }
  };

  const trendInfo = getTrendInfo(trend);

  return (
    <View style={[styles.trendCard, { borderLeftColor: trendInfo.color }]}>
      <View style={styles.trendHeader}>
        <Text style={styles.trendEmoji}>{trendInfo.emoji}</Text>
        <View>
          <Text style={styles.trendTitle}>{title}</Text>
          <Text style={[styles.trendStatus, { color: trendInfo.color }]}>
            {trendInfo.text}
          </Text>
        </View>
      </View>
      {value !== undefined && (
        <Text style={styles.trendValue}>{value.toFixed(1)}/10</Text>
      )}
      {subtitle && <Text style={styles.trendSubtitle}>{subtitle}</Text>}
    </View>
  );
};

const TopItemsCard: React.FC<TopItemsCardProps> = ({ title, items, emoji, maxItems = 5 }) => (
  <View style={styles.topItemsCard}>
    <View style={styles.topItemsHeader}>
      {emoji && <Text style={styles.topItemsEmoji}>{emoji}</Text>}
      <Text style={styles.topItemsTitle}>{title}</Text>
    </View>
    {items.length === 0 ? (
      <Text style={styles.noDataText}>No data available</Text>
    ) : (
      <View style={styles.topItemsList}>
        {items.slice(0, maxItems).map((item, index) => (
          <View key={item.name} style={styles.topItemRow}>
            <View style={styles.topItemInfo}>
              <Text style={styles.topItemName}>{item.name}</Text>
              <Text style={styles.topItemCount}>{item.count} times</Text>
            </View>
            <View style={styles.topItemBar}>
              <View 
                style={[
                  styles.topItemBarFill, 
                  { 
                    width: `${(item.count / items[0].count) * 100}%`,
                    backgroundColor: index === 0 ? '#6366f1' : '#e5e7eb'
                  }
                ]} 
              />
            </View>
          </View>
        ))}
      </View>
    )}
  </View>
);

export default function JournalAnalyticsScreen({ navigation }: Props) {
  const [analytics, setAnalytics] = useState<JournalAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('30d');

  const loadAnalytics = useCallback(async (isRefresh: boolean = false) => {
    try {
      if (!isRefresh) {
        setLoading(true);
      }

      const endDate = new Date();
      const startDate = new Date();
      
      switch (dateRange) {
        case '7d':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case '30d':
          startDate.setDate(endDate.getDate() - 30);
          break;
        case '90d':
          startDate.setDate(endDate.getDate() - 90);
          break;
      }

      const analyticsData = await JournalService.getAnalytics({
        start_date: JournalService.formatDateForAPI(startDate),
        end_date: JournalService.formatDateForAPI(endDate),
      });

      setAnalytics(analyticsData);
    } catch (error: any) {
      console.error('Failed to load analytics:', error);
      Alert.alert('Error', error.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [dateRange]);

  // Refresh analytics when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      loadAnalytics();
    }, [loadAnalytics])
  );

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    loadAnalytics(true);
  }, [loadAnalytics]);

  const handleDateRangeChange = (range: '7d' | '30d' | '90d') => {
    setDateRange(range);
  };

  const getDateRangeLabel = (range: string) => {
    switch (range) {
      case '7d': return 'Last 7 days';
      case '30d': return 'Last 30 days';
      case '90d': return 'Last 90 days';
      default: return 'Last 30 days';
    }
  };

  const getStreakMessage = (streak: number) => {
    if (streak === 0) return 'Start your writing streak today!';
    if (streak === 1) return 'Great start! Keep it going.';
    if (streak < 7) return 'Building momentum!';
    if (streak < 30) return 'Amazing consistency!';
    return 'Incredible dedication!';
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading analytics...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Journal Analytics</Text>
        <Text style={styles.headerSubtitle}>
          Insights into your journaling journey
        </Text>
      </View>

      <ScrollView 
        style={styles.content} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Date Range Selector */}
        <View style={styles.dateRangeContainer}>
          <Text style={styles.dateRangeLabel}>Time Period</Text>
          <View style={styles.dateRangeButtons}>
            {(['7d', '30d', '90d'] as const).map((range) => (
              <TouchableOpacity
                key={range}
                style={[
                  styles.dateRangeButton,
                  dateRange === range && styles.dateRangeButtonActive
                ]}
                onPress={() => handleDateRangeChange(range)}
              >
                <Text style={[
                  styles.dateRangeButtonText,
                  dateRange === range && styles.dateRangeButtonTextActive
                ]}>
                  {getDateRangeLabel(range)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {analytics && (
          <>
            {/* Overview Stats */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Overview</Text>
              <View style={styles.statsGrid}>
                <StatCard
                  title="Total Entries"
                  value={analytics.total_entries}
                  emoji="📝"
                  color="#6366f1"
                />
                <StatCard
                  title="Writing Streak"
                  value={`${analytics.writing_streak} days`}
                  subtitle={getStreakMessage(analytics.writing_streak)}
                  emoji="🔥"
                  color="#f59e0b"
                />
              </View>
            </View>

            {/* Mood Analytics */}
            {analytics.average_mood !== undefined && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Mood Insights</Text>
                <TrendCard
                  title="Average Mood"
                  trend={analytics.mood_trend}
                  value={analytics.average_mood}
                  subtitle={`Your mood is ${analytics.mood_trend} over time`}
                />
              </View>
            )}

            {/* Top Emotions */}
            {analytics.common_emotions.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Most Common Emotions</Text>
                <TopItemsCard
                  title="Emotions"
                  items={analytics.common_emotions.map(item => ({
                    name: item.emotion,
                    count: item.count
                  }))}
                  emoji="😊"
                />
              </View>
            )}

            {/* Top Tags */}
            {analytics.common_tags.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Popular Topics</Text>
                <TopItemsCard
                  title="Tags"
                  items={analytics.common_tags.map(item => ({
                    name: item.tag,
                    count: item.count
                  }))}
                  emoji="🏷️"
                />
              </View>
            )}

            {/* Insights */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Insights</Text>
              <View style={styles.insightsCard}>
                <Text style={styles.insightsTitle}>✨ Personal Reflection</Text>
                <View style={styles.insightsList}>
                  <Text style={styles.insightText}>
                    • You've written {analytics.total_entries} entries in the selected period
                  </Text>
                  {analytics.writing_streak > 0 && (
                    <Text style={styles.insightText}>
                      • Your current writing streak is {analytics.writing_streak} days
                    </Text>
                  )}
                  {analytics.average_mood !== undefined && (
                    <Text style={styles.insightText}>
                      • Your average mood is {analytics.average_mood.toFixed(1)}/10, 
                      which is {analytics.mood_trend}
                    </Text>
                  )}
                  {analytics.common_emotions.length > 0 && (
                    <Text style={styles.insightText}>
                      • Your most frequent emotion is "{analytics.common_emotions[0].emotion}"
                    </Text>
                  )}
                  {analytics.common_tags.length > 0 && (
                    <Text style={styles.insightText}>
                      • You write most about "{analytics.common_tags[0].tag}"
                    </Text>
                  )}
                </View>
              </View>
            </View>
          </>
        )}

        {/* Bottom spacing */}
        <View style={styles.bottomSpacing} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6b7280',
    fontFamily: 'Inter-Regular',
  },
  header: {
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1f2937',
    fontFamily: 'Inter-SemiBold',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
    fontFamily: 'Inter-Regular',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  dateRangeContainer: {
    marginBottom: 24,
  },
  dateRangeLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
    fontFamily: 'Inter-Medium',
  },
  dateRangeButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  dateRangeButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#d1d5db',
    alignItems: 'center',
  },
  dateRangeButtonActive: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1',
  },
  dateRangeButtonText: {
    fontSize: 14,
    color: '#374151',
    fontFamily: 'Inter-Medium',
  },
  dateRangeButtonTextActive: {
    color: '#ffffff',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
    fontFamily: 'Inter-SemiBold',
  },
  statsGrid: {
    gap: 12,
  },
  statCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  statHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statEmoji: {
    fontSize: 18,
    marginRight: 8,
  },
  statTitle: {
    fontSize: 14,
    color: '#6b7280',
    fontFamily: 'Inter-Medium',
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
    fontFamily: 'Inter-SemiBold',
  },
  statSubtitle: {
    fontSize: 12,
    color: '#9ca3af',
    fontFamily: 'Inter-Regular',
  },
  trendCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  trendHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  trendEmoji: {
    fontSize: 24,
    marginRight: 12,
  },
  trendTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    fontFamily: 'Inter-Medium',
  },
  trendStatus: {
    fontSize: 14,
    fontWeight: '500',
    fontFamily: 'Inter-Medium',
  },
  trendValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1f2937',
    marginBottom: 4,
    fontFamily: 'Inter-SemiBold',
  },
  trendSubtitle: {
    fontSize: 12,
    color: '#9ca3af',
    fontFamily: 'Inter-Regular',
  },
  topItemsCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  topItemsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  topItemsEmoji: {
    fontSize: 18,
    marginRight: 8,
  },
  topItemsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    fontFamily: 'Inter-Medium',
  },
  noDataText: {
    fontSize: 14,
    color: '#9ca3af',
    textAlign: 'center',
    fontStyle: 'italic',
    fontFamily: 'Inter-Regular',
  },
  topItemsList: {
    gap: 12,
  },
  topItemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  topItemInfo: {
    flex: 1,
  },
  topItemName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    fontFamily: 'Inter-Medium',
    textTransform: 'capitalize',
  },
  topItemCount: {
    fontSize: 12,
    color: '#6b7280',
    fontFamily: 'Inter-Regular',
  },
  topItemBar: {
    width: 60,
    height: 6,
    backgroundColor: '#f3f4f6',
    borderRadius: 3,
    overflow: 'hidden',
  },
  topItemBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  insightsCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  insightsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
    fontFamily: 'Inter-Medium',
  },
  insightsList: {
    gap: 8,
  },
  insightText: {
    fontSize: 14,
    color: '#4b5563',
    lineHeight: 20,
    fontFamily: 'Inter-Regular',
  },
  bottomSpacing: {
    height: 32,
  },
}); 
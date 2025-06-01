import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  FlatList,
  Alert,
  RefreshControl,
  TextInput,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useFocusEffect } from '@react-navigation/native';
import { RootStackParamList } from '../../../App';
import { JournalService, JournalEntry, JournalEntriesResponse } from '../../services/JournalService';

type JournalScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'Journal'
>;

interface Props {
  navigation: JournalScreenNavigationProp;
}

interface JournalEntryItemProps {
  entry: JournalEntry;
  onPress: (entry: JournalEntry) => void;
  onDelete: (entryId: number) => void;
}

const JournalEntryItem: React.FC<JournalEntryItemProps> = ({ entry, onPress, onDelete }) => {
  const handleDelete = () => {
    Alert.alert(
      'Delete Entry',
      'Are you sure you want to delete this journal entry? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: () => onDelete(entry.id)
        },
      ]
    );
  };

  return (
    <TouchableOpacity style={styles.entryItem} onPress={() => onPress(entry)}>
      <View style={styles.entryHeader}>
        <View style={styles.entryInfo}>
          {entry.title && (
            <Text style={styles.entryTitle} numberOfLines={1}>
              {entry.title}
            </Text>
          )}
          <Text style={styles.entryDate}>
            {JournalService.formatEntryTime(entry.created_at)}
          </Text>
        </View>
        
        {entry.mood_score && (
          <View style={styles.moodBadge}>
            <Text style={styles.moodScore}>{entry.mood_score}/10</Text>
          </View>
        )}
      </View>
      
      <Text style={styles.entryPreview} numberOfLines={2}>
        {JournalService.getContentPreview(entry.content, 120)}
      </Text>
      
      {entry.emotions.length > 0 && (
        <View style={styles.emotionsContainer}>
          {entry.emotions.slice(0, 3).map((emotion, index) => (
            <View key={index} style={styles.emotionTag}>
              <Text style={styles.emotionText}>{emotion}</Text>
            </View>
          ))}
          {entry.emotions.length > 3 && (
            <Text style={styles.moreEmotions}>+{entry.emotions.length - 3} more</Text>
          )}
        </View>
      )}
      
      <TouchableOpacity style={styles.deleteButton} onPress={handleDelete}>
        <Text style={styles.deleteButtonText}>Delete</Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );
};

export default function JournalScreen({ navigation }: Props) {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  const loadEntries = useCallback(async (pageNum: number = 1, search: string = '', isRefresh: boolean = false) => {
    try {
      if (pageNum === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      const response: JournalEntriesResponse = await JournalService.getEntries({
        page: pageNum,
        limit: 20,
        search: search.trim() || undefined,
      });

      if (pageNum === 1 || isRefresh) {
        setEntries(response.entries);
      } else {
        setEntries(prev => [...prev, ...response.entries]);
      }

      setHasMore(response.pagination.has_next);
      setPage(pageNum);
    } catch (error: any) {
      console.error('Failed to load journal entries:', error);
      Alert.alert('Error', error.message || 'Failed to load journal entries');
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  }, []);

  // Refresh entries when screen comes into focus (e.g., after creating a new entry)
  useFocusEffect(
    useCallback(() => {
      console.log('[JournalScreen] Screen focused, refreshing entries');
      loadEntries(1, searchQuery, true);
    }, [searchQuery, loadEntries])
  );

  useEffect(() => {
    loadEntries(1, searchQuery);
  }, [searchQuery]);

  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    loadEntries(1, searchQuery, true);
  }, [searchQuery, loadEntries]);

  const handleLoadMore = useCallback(() => {
    if (hasMore && !loadingMore) {
      loadEntries(page + 1, searchQuery);
    }
  }, [hasMore, loadingMore, page, searchQuery, loadEntries]);

  const handleEntryPress = (entry: JournalEntry) => {
    navigation.navigate('JournalEntry', { entryId: entry.id, isEditing: false });
  };

  const handleDeleteEntry = async (entryId: number) => {
    try {
      await JournalService.deleteEntry(entryId);
      setEntries(prev => prev.filter(entry => entry.id !== entryId));
      // Show success message
      Alert.alert('Success', 'Journal entry deleted successfully');
    } catch (error: any) {
      console.error('Failed to delete journal entry:', error);
      Alert.alert('Error', error.message || 'Failed to delete journal entry');
    }
  };

  const handleCreateEntry = () => {
    navigation.navigate('JournalEntry', { isEditing: true });
  };

  const handleSearchClear = () => {
    setSearchQuery('');
  };

  const renderEntry = ({ item }: { item: JournalEntry }) => (
    <JournalEntryItem
      entry={item}
      onPress={handleEntryPress}
      onDelete={handleDeleteEntry}
    />
  );

  const renderFooter = () => {
    if (!loadingMore) return null;
    
    return (
      <View style={styles.loadingFooter}>
        <Text style={styles.loadingText}>Loading more entries...</Text>
      </View>
    );
  };

  const renderEmpty = () => {
    if (loading) return null;
    
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyEmoji}>📝</Text>
        <Text style={styles.emptyTitle}>
          {searchQuery ? 'No entries found' : 'Start your journal journey'}
        </Text>
        <Text style={styles.emptySubtitle}>
          {searchQuery 
            ? 'Try adjusting your search terms'
            : 'Write your first journal entry to begin tracking your thoughts and feelings'
          }
        </Text>
        {!searchQuery && (
          <TouchableOpacity style={styles.createFirstButton} onPress={handleCreateEntry}>
            <Text style={styles.createFirstButtonText}>Write First Entry</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header with Search */}
      <View style={styles.header}>
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search your journal entries..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            returnKeyType="search"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity style={styles.clearButton} onPress={handleSearchClear}>
              <Text style={styles.clearButtonText}>✕</Text>
            </TouchableOpacity>
          )}
        </View>
        
        <TouchableOpacity style={styles.createButton} onPress={handleCreateEntry}>
          <Text style={styles.createButtonText}>+ New Entry</Text>
        </TouchableOpacity>
      </View>

      {/* Journal Entries List */}
      <FlatList
        data={entries}
        renderItem={renderEntry}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.3}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    position: 'relative',
  },
  searchInput: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingRight: 40,
    fontSize: 16,
    fontFamily: 'Inter-Regular',
    backgroundColor: '#f9fafb',
  },
  clearButton: {
    position: 'absolute',
    right: 10,
    padding: 4,
  },
  clearButtonText: {
    fontSize: 16,
    color: '#6b7280',
  },
  createButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  createButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'Inter-Medium',
  },
  listContainer: {
    padding: 16,
  },
  entryItem: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    position: 'relative',
  },
  entryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  entryInfo: {
    flex: 1,
  },
  entryTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
    fontFamily: 'Inter-Medium',
  },
  entryDate: {
    fontSize: 12,
    color: '#6b7280',
    fontFamily: 'Inter-Regular',
  },
  moodBadge: {
    backgroundColor: '#f0f9ff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  moodScore: {
    fontSize: 12,
    color: '#0ea5e9',
    fontWeight: '600',
    fontFamily: 'Inter-Medium',
  },
  entryPreview: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginBottom: 8,
    fontFamily: 'Inter-Regular',
  },
  emotionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    marginBottom: 8,
  },
  emotionTag: {
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 6,
    marginBottom: 4,
  },
  emotionText: {
    fontSize: 12,
    color: '#4b5563',
    fontFamily: 'Inter-Regular',
  },
  moreEmotions: {
    fontSize: 12,
    color: '#6b7280',
    fontStyle: 'italic',
    fontFamily: 'Inter-Regular',
  },
  deleteButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    padding: 4,
  },
  deleteButtonText: {
    fontSize: 12,
    color: '#ef4444',
    fontFamily: 'Inter-Regular',
  },
  loadingFooter: {
    padding: 16,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 14,
    color: '#6b7280',
    fontFamily: 'Inter-Regular',
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
    paddingHorizontal: 32,
  },
  emptyEmoji: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 8,
    fontFamily: 'Inter-Medium',
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 24,
    fontFamily: 'Inter-Regular',
  },
  createFirstButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  createFirstButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'Inter-Medium',
  },
}); 
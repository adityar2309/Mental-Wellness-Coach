import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TextInput,
  Alert,
  Modal,
  FlatList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../../../App';
import { 
  JournalService, 
  JournalEntry, 
  CreateJournalEntryRequest,
  UpdateJournalEntryRequest,
  JournalPrompt 
} from '../../services/JournalService';

type JournalEntryScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'JournalEntry'
>;

type JournalEntryScreenRouteProp = RouteProp<
  RootStackParamList,
  'JournalEntry'
>;

interface Props {
  navigation: JournalEntryScreenNavigationProp;
  route: JournalEntryScreenRouteProp;
}

interface EmotionChip {
  emotion: string;
  isSelected: boolean;
}

interface TagChip {
  tag: string;
  isSelected: boolean;
}

const COMMON_EMOTIONS = [
  'happy', 'sad', 'angry', 'anxious', 'calm', 'excited', 'grateful', 'frustrated',
  'hopeful', 'lonely', 'confident', 'overwhelmed', 'peaceful', 'worried', 'content'
];

const COMMON_TAGS = [
  'work', 'family', 'relationships', 'health', 'personal growth', 'stress',
  'goals', 'gratitude', 'reflection', 'challenges', 'achievements', 'future'
];

export default function JournalEntryScreen({ navigation, route }: Props) {
  const { entryId, isEditing } = route.params;
  const isCreateMode = isEditing && !entryId;
  const isEditMode = isEditing && !!entryId;
  const isViewMode = !isEditing;

  // Form state
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [moodScore, setMoodScore] = useState<number | undefined>(undefined);
  const [emotions, setEmotions] = useState<EmotionChip[]>(
    COMMON_EMOTIONS.map(emotion => ({ emotion, isSelected: false }))
  );
  const [tags, setTags] = useState<TagChip[]>(
    COMMON_TAGS.map(tag => ({ tag, isSelected: false }))
  );
  const [isPrivate, setIsPrivate] = useState(true);

  // UI state
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showPrompts, setShowPrompts] = useState(false);
  const [prompts, setPrompts] = useState<JournalPrompt[]>([]);
  const [loadingPrompts, setLoadingPrompts] = useState(false);

  // Load existing entry if editing
  useEffect(() => {
    if (entryId && !isCreateMode) {
      loadEntry();
    }
  }, [entryId, isCreateMode]);

  const loadEntry = async () => {
    if (!entryId) return;
    
    try {
      setLoading(true);
      const entry = await JournalService.getEntry(entryId);
      
      setTitle(entry.title || '');
      setContent(entry.content);
      setMoodScore(entry.mood_score);
      setIsPrivate(entry.is_private);
      
      // Update emotions
      setEmotions(prev => prev.map(emotionChip => ({
        ...emotionChip,
        isSelected: entry.emotions.includes(emotionChip.emotion)
      })));
      
      // Update tags
      setTags(prev => prev.map(tagChip => ({
        ...tagChip,
        isSelected: entry.tags.includes(tagChip.tag)
      })));
      
    } catch (error: any) {
      console.error('Failed to load journal entry:', error);
      Alert.alert('Error', error.message || 'Failed to load journal entry', [
        { text: 'OK', onPress: () => navigation.navigate('Journal') }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadPrompts = async () => {
    try {
      setLoadingPrompts(true);
      const promptsData = await JournalService.getPrompts({
        count: 5,
        mood: moodScore
      });
      setPrompts(promptsData);
    } catch (error: any) {
      console.error('Failed to load prompts:', error);
      Alert.alert('Error', error.message || 'Failed to load writing prompts');
    } finally {
      setLoadingPrompts(false);
    }
  };

  const handleSave = async () => {
    // Validate input
    const selectedEmotions = emotions.filter(e => e.isSelected).map(e => e.emotion);
    const selectedTags = tags.filter(t => t.isSelected).map(t => t.tag);
    
    const entryData = {
      title: title.trim() || undefined,
      content: content.trim(),
      mood_score: moodScore,
      emotions: selectedEmotions,
      tags: selectedTags,
      is_private: isPrivate
    };

    // Validate using JournalService
    const validation = JournalService.validateEntry(entryData);
    if (!validation.isValid) {
      Alert.alert('Validation Error', validation.errors.join('\n'));
      return;
    }

    try {
      setSaving(true);
      
      if (isCreateMode) {
        // Create new entry
        await JournalService.createEntry(entryData as CreateJournalEntryRequest);
        Alert.alert('Success', 'Journal entry created successfully!', [
          { text: 'OK', onPress: () => navigation.navigate('Journal') }
        ]);
      } else if (isEditMode && entryId) {
        // Update existing entry
        await JournalService.updateEntry(entryId, entryData as UpdateJournalEntryRequest);
        Alert.alert('Success', 'Journal entry updated successfully!', [
          { text: 'OK', onPress: () => navigation.navigate('Journal') }
        ]);
      }
    } catch (error: any) {
      console.error('Failed to save journal entry:', error);
      Alert.alert('Error', error.message || 'Failed to save journal entry');
    } finally {
      setSaving(false);
    }
  };

  const handleEmotionToggle = (emotionIndex: number) => {
    if (!isEditing) return;
    
    setEmotions(prev => prev.map((emotion, index) => 
      index === emotionIndex 
        ? { ...emotion, isSelected: !emotion.isSelected }
        : emotion
    ));
  };

  const handleTagToggle = (tagIndex: number) => {
    if (!isEditing) return;
    
    setTags(prev => prev.map((tag, index) => 
      index === tagIndex 
        ? { ...tag, isSelected: !tag.isSelected }
        : tag
    ));
  };

  const handleMoodSelect = (score: number) => {
    if (!isEditing) return;
    setMoodScore(score === moodScore ? undefined : score);
  };

  const handlePromptSelect = (prompt: JournalPrompt) => {
    setContent(prev => {
      const newContent = prev ? `${prev}\n\n${prompt.text}\n\n` : `${prompt.text}\n\n`;
      return newContent;
    });
    setShowPrompts(false);
  };

  const handleCancel = () => {
    if (content.trim() || title.trim()) {
      Alert.alert(
        'Discard Changes',
        'You have unsaved changes. Are you sure you want to discard them?',
        [
          { text: 'Keep Editing', style: 'cancel' },
          { text: 'Discard', style: 'destructive', onPress: () => navigation.navigate('Journal') }
        ]
      );
    } else {
      navigation.navigate('Journal');
    }
  };

  const renderMoodSelector = () => {
    if (!isEditing && moodScore === undefined) return null;
    
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Mood (1-10)</Text>
        <View style={styles.moodContainer}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((score) => (
            <TouchableOpacity
              key={score}
              style={[
                styles.moodButton,
                moodScore === score && styles.moodButtonSelected,
                !isEditing && styles.moodButtonDisabled
              ]}
              onPress={() => handleMoodSelect(score)}
              disabled={!isEditing}
            >
              <Text style={[
                styles.moodButtonText,
                moodScore === score && styles.moodButtonTextSelected
              ]}>
                {score}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    );
  };

  const renderEmotionChips = () => {
    const selectedEmotions = emotions.filter(e => e.isSelected);
    if (!isEditing && selectedEmotions.length === 0) return null;
    
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Emotions</Text>
        <View style={styles.chipContainer}>
          {emotions.map((emotion, index) => {
            if (!isEditing && !emotion.isSelected) return null;
            
            return (
              <TouchableOpacity
                key={emotion.emotion}
                style={[
                  styles.chip,
                  emotion.isSelected && styles.chipSelected,
                  !isEditing && styles.chipDisabled
                ]}
                onPress={() => handleEmotionToggle(index)}
                disabled={!isEditing}
              >
                <Text style={[
                  styles.chipText,
                  emotion.isSelected && styles.chipTextSelected
                ]}>
                  {emotion.emotion}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    );
  };

  const renderTagChips = () => {
    const selectedTags = tags.filter(t => t.isSelected);
    if (!isEditing && selectedTags.length === 0) return null;
    
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tags</Text>
        <View style={styles.chipContainer}>
          {tags.map((tag, index) => {
            if (!isEditing && !tag.isSelected) return null;
            
            return (
              <TouchableOpacity
                key={tag.tag}
                style={[
                  styles.chip,
                  tag.isSelected && styles.chipSelected,
                  !isEditing && styles.chipDisabled
                ]}
                onPress={() => handleTagToggle(index)}
                disabled={!isEditing}
              >
                <Text style={[
                  styles.chipText,
                  tag.isSelected && styles.chipTextSelected
                ]}>
                  {tag.tag}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    );
  };

  const renderPromptModal = () => (
    <Modal
      visible={showPrompts}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Writing Prompts</Text>
          <TouchableOpacity onPress={() => setShowPrompts(false)}>
            <Text style={styles.modalCloseButton}>✕</Text>
          </TouchableOpacity>
        </View>
        
        {loadingPrompts ? (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Loading prompts...</Text>
          </View>
        ) : (
          <FlatList
            data={prompts}
            keyExtractor={(item) => item.id || item.text}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.promptItem}
                onPress={() => handlePromptSelect(item)}
              >
                <Text style={styles.promptText}>{item.text}</Text>
              </TouchableOpacity>
            )}
            contentContainerStyle={styles.promptsList}
          />
        )}
      </SafeAreaView>
    </Modal>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading journal entry...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={handleCancel} style={styles.headerButton}>
            <Text style={styles.headerButtonText}>Cancel</Text>
          </TouchableOpacity>
          
          <Text style={styles.headerTitle}>
            {isCreateMode ? 'New Entry' : isEditMode ? 'Edit Entry' : 'Journal Entry'}
          </Text>
          
          {isEditing && (
            <TouchableOpacity 
              onPress={handleSave} 
              style={[styles.headerButton, styles.saveButton]}
              disabled={saving}
            >
              <Text style={styles.saveButtonText}>
                {saving ? 'Saving...' : 'Save'}
              </Text>
            </TouchableOpacity>
          )}
          
          {isViewMode && (
            <TouchableOpacity 
              onPress={() => navigation.setParams({ isEditing: true })}
              style={styles.headerButton}
            >
              <Text style={styles.headerButtonText}>Edit</Text>
            </TouchableOpacity>
          )}
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Title Input */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Title (Optional)</Text>
            <TextInput
              style={[styles.titleInput, !isEditing && styles.inputDisabled]}
              placeholder="Give your entry a title..."
              value={title}
              onChangeText={setTitle}
              maxLength={200}
              editable={isEditing}
            />
          </View>

          {/* Content Input */}
          <View style={styles.section}>
            <View style={styles.contentHeader}>
              <Text style={styles.sectionTitle}>Your Journal Entry</Text>
              {isEditing && (
                <TouchableOpacity 
                  style={styles.promptButton}
                  onPress={() => {
                    setShowPrompts(true);
                    loadPrompts();
                  }}
                >
                  <Text style={styles.promptButtonText}>✨ Get Prompts</Text>
                </TouchableOpacity>
              )}
            </View>
            <TextInput
              style={[styles.contentInput, !isEditing && styles.inputDisabled]}
              placeholder="What's on your mind today? How are you feeling? What happened that you want to remember or reflect on?"
              value={content}
              onChangeText={setContent}
              multiline
              textAlignVertical="top"
              maxLength={10000}
              editable={isEditing}
            />
            <Text style={styles.characterCount}>
              {content.length}/10,000 characters
            </Text>
          </View>

          {/* Mood Selector */}
          {renderMoodSelector()}

          {/* Emotion Chips */}
          {renderEmotionChips()}

          {/* Tag Chips */}
          {renderTagChips()}

          {/* Privacy Toggle */}
          {isEditing && (
            <View style={styles.section}>
              <TouchableOpacity 
                style={styles.privacyToggle}
                onPress={() => setIsPrivate(!isPrivate)}
              >
                <View style={styles.privacyInfo}>
                  <Text style={styles.sectionTitle}>Privacy</Text>
                  <Text style={styles.privacySubtitle}>
                    {isPrivate ? 'Private - Only you can see this entry' : 'Shared - Visible to your care team'}
                  </Text>
                </View>
                <View style={[styles.toggle, isPrivate && styles.toggleActive]}>
                  <View style={[styles.toggleButton, isPrivate && styles.toggleButtonActive]} />
                </View>
              </TouchableOpacity>
            </View>
          )}
        </ScrollView>

        {renderPromptModal()}
      </KeyboardAvoidingView>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerButton: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    minWidth: 60,
  },
  headerButtonText: {
    fontSize: 16,
    color: '#6366f1',
    fontFamily: 'Inter-Medium',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    fontFamily: 'Inter-SemiBold',
  },
  saveButton: {
    backgroundColor: '#6366f1',
    borderRadius: 8,
  },
  saveButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'Inter-Medium',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
    fontFamily: 'Inter-Medium',
  },
  titleInput: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    fontFamily: 'Inter-Regular',
  },
  contentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  promptButton: {
    backgroundColor: '#f0f9ff',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  promptButtonText: {
    fontSize: 12,
    color: '#0ea5e9',
    fontWeight: '600',
    fontFamily: 'Inter-Medium',
  },
  contentInput: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    minHeight: 200,
    fontFamily: 'Inter-Regular',
  },
  characterCount: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'right',
    marginTop: 4,
    fontFamily: 'Inter-Regular',
  },
  inputDisabled: {
    backgroundColor: '#f9fafb',
    color: '#6b7280',
  },
  moodContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  moodButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: '#d1d5db',
    justifyContent: 'center',
    alignItems: 'center',
  },
  moodButtonSelected: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1',
  },
  moodButtonDisabled: {
    opacity: 0.6,
  },
  moodButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    fontFamily: 'Inter-Medium',
  },
  moodButtonTextSelected: {
    color: '#ffffff',
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  chipSelected: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1',
  },
  chipDisabled: {
    opacity: 0.6,
  },
  chipText: {
    fontSize: 14,
    color: '#374151',
    fontFamily: 'Inter-Regular',
  },
  chipTextSelected: {
    color: '#ffffff',
  },
  privacyToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#d1d5db',
  },
  privacyInfo: {
    flex: 1,
  },
  privacySubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
    fontFamily: 'Inter-Regular',
  },
  toggle: {
    width: 44,
    height: 24,
    backgroundColor: '#d1d5db',
    borderRadius: 12,
    justifyContent: 'center',
    paddingHorizontal: 2,
  },
  toggleActive: {
    backgroundColor: '#6366f1',
  },
  toggleButton: {
    width: 20,
    height: 20,
    backgroundColor: '#ffffff',
    borderRadius: 10,
    alignSelf: 'flex-start',
  },
  toggleButtonActive: {
    alignSelf: 'flex-end',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    fontFamily: 'Inter-SemiBold',
  },
  modalCloseButton: {
    fontSize: 18,
    color: '#6b7280',
    padding: 4,
  },
  promptsList: {
    padding: 16,
  },
  promptItem: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  promptText: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
    fontFamily: 'Inter-Regular',
  },
}); 
/**
 * Mental Wellness Coach - Journal Service
 * 
 * Service for managing journal entries, prompts, and analytics.
 */

import { ApiClient } from './ApiClient';

export interface JournalEntry {
  id: number;
  title?: string;
  content: string;
  mood_score?: number;
  emotions: string[];
  tags: string[];
  is_private: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateJournalEntryRequest {
  title?: string;
  content: string;
  mood_score?: number;
  emotions?: string[];
  tags?: string[];
  is_private?: boolean;
}

export interface UpdateJournalEntryRequest {
  title?: string;
  content?: string;
  mood_score?: number;
  emotions?: string[];
  tags?: string[];
  is_private?: boolean;
}

export interface JournalEntriesResponse {
  entries: JournalEntry[];
  pagination: {
    page: number;
    pages: number;
    per_page: number;
    total: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface JournalPrompt {
  id?: string;
  text: string;
  topic?: string;
}

export interface JournalAnalytics {
  total_entries: number;
  average_mood?: number;
  mood_trend: 'improving' | 'declining' | 'stable';
  common_emotions: Array<{ emotion: string; count: number }>;
  common_tags: Array<{ tag: string; count: number }>;
  writing_streak: number;
  date_range: {
    start_date: string;
    end_date: string;
  };
}

export class JournalService {
  /**
   * Get journal entries for the current user.
   * 
   * Args:
   *   options: Query options for filtering and pagination
   * 
   * Returns:
   *   Promise<JournalEntriesResponse>: Paginated journal entries
   */
  static async getEntries(options: {
    page?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
    search?: string;
  } = {}): Promise<JournalEntriesResponse> {
    try {
      const params = new URLSearchParams();
      
      if (options.page) params.append('page', options.page.toString());
      if (options.limit) params.append('limit', options.limit.toString());
      if (options.start_date) params.append('start_date', options.start_date);
      if (options.end_date) params.append('end_date', options.end_date);
      if (options.search) params.append('search', options.search);
      
      const queryString = params.toString();
      const endpoint = `/journal/entries${queryString ? `?${queryString}` : ''}`;
      
      const response = await ApiClient.get(endpoint);
      return response.data;
    } catch (error: any) {
      console.error('[JournalService] Failed to get entries:', error);
      throw new Error(error.message || 'Failed to get journal entries');
    }
  }

  /**
   * Create a new journal entry.
   * 
   * Args:
   *   entryData: Journal entry data
   * 
   * Returns:
   *   Promise<JournalEntry>: Created journal entry
   */
  static async createEntry(entryData: CreateJournalEntryRequest): Promise<JournalEntry> {
    try {
      const response = await ApiClient.post('/journal/entries', entryData);
      return response.data;
    } catch (error: any) {
      console.error('[JournalService] Failed to create entry:', error);
      throw new Error(error.message || 'Failed to create journal entry');
    }
  }

  /**
   * Get a specific journal entry by ID.
   * 
   * Args:
   *   entryId: ID of the journal entry
   * 
   * Returns:
   *   Promise<JournalEntry>: Journal entry
   */
  static async getEntry(entryId: number): Promise<JournalEntry> {
    try {
      const response = await ApiClient.get(`/journal/entries/${entryId}`);
      return response.data;
    } catch (error: any) {
      console.error('[JournalService] Failed to get entry:', error);
      throw new Error(error.message || 'Failed to get journal entry');
    }
  }

  /**
   * Update a journal entry.
   * 
   * Args:
   *   entryId: ID of the journal entry
   *   updateData: Updated journal entry data
   * 
   * Returns:
   *   Promise<JournalEntry>: Updated journal entry
   */
  static async updateEntry(entryId: number, updateData: UpdateJournalEntryRequest): Promise<JournalEntry> {
    try {
      const response = await ApiClient.put(`/journal/entries/${entryId}`, updateData);
      return response.data;
    } catch (error: any) {
      console.error('[JournalService] Failed to update entry:', error);
      throw new Error(error.message || 'Failed to update journal entry');
    }
  }

  /**
   * Delete a journal entry.
   * 
   * Args:
   *   entryId: ID of the journal entry
   * 
   * Returns:
   *   Promise<void>
   */
  static async deleteEntry(entryId: number): Promise<void> {
    try {
      await ApiClient.delete(`/journal/entries/${entryId}`);
    } catch (error: any) {
      console.error('[JournalService] Failed to delete entry:', error);
      throw new Error(error.message || 'Failed to delete journal entry');
    }
  }

  /**
   * Get journal writing prompts.
   * 
   * Args:
   *   options: Prompt generation options
   * 
   * Returns:
   *   Promise<JournalPrompt[]>: Array of journal prompts
   */
  static async getPrompts(options: {
    count?: number;
    mood?: number;
    topic?: string;
  } = {}): Promise<JournalPrompt[]> {
    try {
      const params = new URLSearchParams();
      
      if (options.count) params.append('count', options.count.toString());
      if (options.mood) params.append('mood', options.mood.toString());
      if (options.topic) params.append('topic', options.topic);
      
      const queryString = params.toString();
      const endpoint = `/journal/prompts${queryString ? `?${queryString}` : ''}`;
      
      const response = await ApiClient.get(endpoint);
      
      // Convert prompt strings to JournalPrompt objects
      const prompts: JournalPrompt[] = response.data.prompts.map((text: string, index: number) => ({
        id: `prompt_${index}`,
        text,
        topic: options.topic
      }));
      
      return prompts;
    } catch (error: any) {
      console.error('[JournalService] Failed to get prompts:', error);
      throw new Error(error.message || 'Failed to get journal prompts');
    }
  }

  /**
   * Get journal analytics and insights.
   * 
   * Args:
   *   options: Analytics date range options
   * 
   * Returns:
   *   Promise<JournalAnalytics>: Journal analytics data
   */
  static async getAnalytics(options: {
    start_date?: string;
    end_date?: string;
  } = {}): Promise<JournalAnalytics> {
    try {
      const params = new URLSearchParams();
      
      if (options.start_date) params.append('start_date', options.start_date);
      if (options.end_date) params.append('end_date', options.end_date);
      
      const queryString = params.toString();
      const endpoint = `/journal/analytics${queryString ? `?${queryString}` : ''}`;
      
      const response = await ApiClient.get(endpoint);
      return response.data;
    } catch (error: any) {
      console.error('[JournalService] Failed to get analytics:', error);
      throw new Error(error.message || 'Failed to get journal analytics');
    }
  }

  /**
   * Format a date for API requests (YYYY-MM-DD format).
   * 
   * Args:
   *   date: Date object or date string
   * 
   * Returns:
   *   string: Formatted date string
   */
  static formatDateForAPI(date: Date | string): string {
    try {
      const dateObj = typeof date === 'string' ? new Date(date) : date;
      return dateObj.toISOString().split('T')[0];
    } catch (error) {
      console.error('[JournalService] Failed to format date:', error);
      return new Date().toISOString().split('T')[0];
    }
  }

  /**
   * Format a timestamp for display in journal entries.
   * 
   * Args:
   *   timestamp: ISO timestamp string
   * 
   * Returns:
   *   string: Formatted time string
   */
  static formatEntryTime(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      
      // Check if date is invalid
      if (isNaN(date.getTime())) {
        return 'Unknown time';
      }
      
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffMins < 1) {
        return 'Just now';
      } else if (diffMins < 60) {
        return `${diffMins} min ago`;
      } else if (diffHours < 24) {
        return `${diffHours}h ago`;
      } else if (diffDays < 7) {
        return `${diffDays}d ago`;
      } else {
        // For longer periods, show the actual date
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        });
      }
    } catch (error) {
      console.error('[JournalService] Failed to format timestamp:', error);
      return 'Unknown time';
    }
  }

  /**
   * Get a preview of journal entry content (truncated).
   * 
   * Args:
   *   content: Full journal entry content
   *   maxLength: Maximum length for preview (default: 150)
   * 
   * Returns:
   *   string: Truncated content preview
   */
  static getContentPreview(content: string, maxLength: number = 150): string {
    if (!content) return '';
    
    if (content.length <= maxLength) {
      return content;
    }
    
    // Find the last complete word within the limit
    const truncated = content.substring(0, maxLength);
    const lastSpaceIndex = truncated.lastIndexOf(' ');
    
    if (lastSpaceIndex > 0) {
      return truncated.substring(0, lastSpaceIndex) + '...';
    }
    
    return truncated + '...';
  }

  /**
   * Validate journal entry data before submission.
   * 
   * Args:
   *   entryData: Journal entry data to validate
   * 
   * Returns:
   *   Object with isValid boolean and errors array
   */
  static validateEntry(entryData: CreateJournalEntryRequest | UpdateJournalEntryRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    
    // Check content (required for create, optional for update)
    if ('content' in entryData && entryData.content !== undefined) {
      if (!entryData.content || entryData.content.trim().length === 0) {
        errors.push('Content is required');
      } else if (entryData.content.length > 10000) {
        errors.push('Content must be less than 10,000 characters');
      }
    }
    
    // Check title length
    if (entryData.title && entryData.title.length > 200) {
      errors.push('Title must be less than 200 characters');
    }
    
    // Check mood score
    if (entryData.mood_score !== undefined && entryData.mood_score !== null) {
      if (!Number.isInteger(entryData.mood_score) || entryData.mood_score < 1 || entryData.mood_score > 10) {
        errors.push('Mood score must be an integer between 1 and 10');
      }
    }
    
    // Check emotions array
    if (entryData.emotions && !Array.isArray(entryData.emotions)) {
      errors.push('Emotions must be an array');
    }
    
    // Check tags array
    if (entryData.tags && !Array.isArray(entryData.tags)) {
      errors.push('Tags must be an array');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

export default JournalService; 
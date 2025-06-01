import * as SecureStore from 'expo-secure-store';

// Configuration
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:3000/api'  // Development
  : 'https://api.mentalwellnesscoach.ai/api';  // Production

const DEFAULT_TIMEOUT = 10000; // 10 seconds

export interface ApiError {
  message: string;
  status: number;
  data?: any;
}

export interface ApiResponse<T = any> {
  status: string;
  data?: T;
  message?: string;
  error?: string;
}

/**
 * HTTP Client for API communication with automatic authentication
 */
export class ApiClient {
  private static baseURL = API_BASE_URL;

  /**
   * Set custom base URL (useful for testing)
   */
  static setBaseURL(url: string): void {
    this.baseURL = url;
  }

  /**
   * Get authentication headers
   */
  private static async getAuthHeaders(): Promise<Record<string, string>> {
    const token = await SecureStore.getItemAsync('access_token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Make HTTP request with error handling
   */
  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = await this.getAuthHeaders();

    const requestOptions: RequestInit = {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
      signal: AbortSignal.timeout(DEFAULT_TIMEOUT),
    };

    try {
      console.log(`[API] ${options.method || 'GET'} ${url}`);
      
      const response = await fetch(url, requestOptions);
      const data = await response.json();

      if (!response.ok) {
        const error: ApiError = {
          message: data.message || data.error || 'Request failed',
          status: response.status,
          data: data,
        };
        throw error;
      }

      console.log(`[API] ${options.method || 'GET'} ${url} - Success`);
      return data;

    } catch (error) {
      console.error(`[API] ${options.method || 'GET'} ${url} - Error:`, error);
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      if (error && typeof error === 'object' && 'status' in error) {
        throw error; // Re-throw API errors
      }
      
      throw new Error('Network error. Please check your connection.');
    }
  }

  /**
   * GET request
   */
  static async get<T = any>(endpoint: string): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'GET',
    });
  }

  /**
   * POST request
   */
  static async post<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  static async put<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  static async delete<T = any>(endpoint: string): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'DELETE',
    });
  }

  /**
   * PATCH request
   */
  static async patch<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

/**
 * Mood API endpoints
 */
export class MoodApi {
  static async createEntry(data: {
    mood_score: number;
    energy_level?: number;
    stress_level?: number;
    sleep_quality?: number;
    notes?: string;
  }) {
    return ApiClient.post('/mood/entries', data);
  }

  static async getEntries(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    return ApiClient.get(`/mood/entries${queryString ? `?${queryString}` : ''}`);
  }

  static async getAnalytics(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    return ApiClient.get(`/mood/analytics${queryString ? `?${queryString}` : ''}`);
  }

  static async quickCheckIn(moodScore: number) {
    return ApiClient.post('/mood/quick-checkin', { mood_score: moodScore });
  }
}

/**
 * Conversation API endpoints
 */
export class ConversationApi {
  static async startConversation() {
    return ApiClient.post('/conversations/start');
  }

  static async sendMessage(conversationId: string, message: string) {
    return ApiClient.post(`/conversations/${conversationId}/messages`, {
      content: message,
    });
  }

  static async getMessages(conversationId: string) {
    return ApiClient.get(`/conversations/${conversationId}/messages`);
  }

  static async getConversations() {
    return ApiClient.get('/conversations');
  }
}

/**
 * Crisis API endpoints
 */
export class CrisisApi {
  static async analyzeContent(content: string) {
    return ApiClient.post('/crisis/analyze', { content });
  }

  static async getResources() {
    return ApiClient.get('/crisis/resources');
  }

  static async getEmergencyContacts() {
    return ApiClient.get('/crisis/emergency-contacts');
  }
} 
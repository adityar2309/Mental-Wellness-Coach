import { ApiClient } from './ApiClient';

export interface MindfulnessSession {
  id: number;
  session_type: 'breathing' | 'meditation' | 'body_scan' | 'progressive_relaxation';
  title: string;
  description?: string;
  duration_minutes: number;
  completed_duration_minutes?: number;
  completed: boolean;
  effectiveness_rating?: number;
  mood_before?: number;
  mood_after?: number;
  stress_before?: number;
  stress_after?: number;
  notes?: string;
  session_data?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}

export interface SessionTemplate {
  title: string;
  description: string;
  duration_minutes: number;
  instructions: string;
}

export interface SessionTemplates {
  breathing: SessionTemplate[];
  meditation: SessionTemplate[];
  body_scan: SessionTemplate[];
  progressive_relaxation: SessionTemplate[];
}

export interface CreateSessionData {
  session_type: 'breathing' | 'meditation' | 'body_scan' | 'progressive_relaxation';
  title: string;
  description?: string;
  duration_minutes: number;
  mood_before?: number;
  stress_before?: number;
}

export interface UpdateSessionData {
  completed?: boolean;
  completed_duration_minutes?: number;
  mood_after?: number;
  stress_after?: number;
  effectiveness_rating?: number;
  notes?: string;
  session_data?: Record<string, any>;
}

export interface MindfulnessAnalytics {
  period_days: number;
  total_sessions: number;
  completed_sessions: number;
  completion_rate: number;
  total_minutes: number;
  average_effectiveness?: number;
  average_mood_improvement?: number;
  average_stress_reduction?: number;
  session_types: Record<string, number>;
  streak_days: number;
}

export interface SessionsResponse {
  sessions: MindfulnessSession[];
  total: number;
}

export interface SessionResponse {
  session: MindfulnessSession;
}

export interface TemplatesResponse {
  templates: SessionTemplates;
}

export interface AnalyticsResponse {
  analytics: MindfulnessAnalytics;
}

export interface CreateSessionResponse {
  message: string;
  session: MindfulnessSession;
}

export interface UpdateSessionResponse {
  message: string;
  session: MindfulnessSession;
}

export interface DeleteSessionResponse {
  message: string;
}

export class MindfulnessService {
  /**
   * Get all mindfulness sessions for the current user
   */
  static async getSessions(options?: {
    session_type?: string;
    completed?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<SessionsResponse> {
    try {
      const queryParams = new URLSearchParams();
      
      if (options?.session_type) {
        queryParams.append('session_type', options.session_type);
      }
      if (options?.completed !== undefined) {
        queryParams.append('completed', options.completed.toString());
      }
      if (options?.limit) {
        queryParams.append('limit', options.limit.toString());
      }
      if (options?.offset) {
        queryParams.append('offset', options.offset.toString());
      }

      const url = `/mindfulness/sessions${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      return await ApiClient.get<SessionsResponse>(url);
    } catch (error) {
      console.error('Error fetching mindfulness sessions:', error);
      throw new Error('Failed to fetch mindfulness sessions');
    }
  }

  /**
   * Create a new mindfulness session
   */
  static async createSession(data: CreateSessionData): Promise<CreateSessionResponse> {
    try {
      return await ApiClient.post<CreateSessionResponse>('/mindfulness/sessions', data);
    } catch (error) {
      console.error('Error creating mindfulness session:', error);
      throw new Error('Failed to create mindfulness session');
    }
  }

  /**
   * Get a specific mindfulness session by ID
   */
  static async getSession(sessionId: number): Promise<SessionResponse> {
    try {
      return await ApiClient.get<SessionResponse>(`/mindfulness/sessions/${sessionId}`);
    } catch (error) {
      console.error('Error fetching mindfulness session:', error);
      throw new Error('Failed to fetch mindfulness session');
    }
  }

  /**
   * Update a mindfulness session (typically to complete it)
   */
  static async updateSession(sessionId: number, data: UpdateSessionData): Promise<UpdateSessionResponse> {
    try {
      return await ApiClient.put<UpdateSessionResponse>(`/mindfulness/sessions/${sessionId}`, data);
    } catch (error) {
      console.error('Error updating mindfulness session:', error);
      throw new Error('Failed to update mindfulness session');
    }
  }

  /**
   * Delete a mindfulness session
   */
  static async deleteSession(sessionId: number): Promise<DeleteSessionResponse> {
    try {
      return await ApiClient.delete<DeleteSessionResponse>(`/mindfulness/sessions/${sessionId}`);
    } catch (error) {
      console.error('Error deleting mindfulness session:', error);
      throw new Error('Failed to delete mindfulness session');
    }
  }

  /**
   * Get predefined session templates
   */
  static async getTemplates(): Promise<TemplatesResponse> {
    try {
      return await ApiClient.get<TemplatesResponse>('/mindfulness/templates');
    } catch (error) {
      console.error('Error fetching session templates:', error);
      throw new Error('Failed to fetch session templates');
    }
  }

  /**
   * Get mindfulness analytics for the user
   */
  static async getAnalytics(days?: number): Promise<AnalyticsResponse> {
    try {
      const url = `/mindfulness/analytics${days ? `?days=${days}` : ''}`;
      return await ApiClient.get<AnalyticsResponse>(url);
    } catch (error) {
      console.error('Error fetching mindfulness analytics:', error);
      throw new Error('Failed to fetch mindfulness analytics');
    }
  }

  /**
   * Start a mindfulness session with pre-session mood tracking
   */
  static async startSession(template: SessionTemplate, preSessionData: {
    mood_before?: number;
    stress_before?: number;
  }): Promise<CreateSessionResponse> {
    try {
      const sessionData: CreateSessionData = {
        session_type: 'meditation', // Default, should be passed from template
        title: template.title,
        description: template.description,
        duration_minutes: template.duration_minutes,
        mood_before: preSessionData.mood_before,
        stress_before: preSessionData.stress_before,
      };

      return await this.createSession(sessionData);
    } catch (error) {
      console.error('Error starting mindfulness session:', error);
      throw new Error('Failed to start mindfulness session');
    }
  }

  /**
   * Complete a mindfulness session with post-session tracking
   */
  static async completeSession(sessionId: number, completionData: {
    completed_duration_minutes: number;
    mood_after?: number;
    stress_after?: number;
    effectiveness_rating?: number;
    notes?: string;
    session_data?: Record<string, any>;
  }): Promise<UpdateSessionResponse> {
    try {
      const updateData: UpdateSessionData = {
        completed: true,
        ...completionData,
      };

      return await this.updateSession(sessionId, updateData);
    } catch (error) {
      console.error('Error completing mindfulness session:', error);
      throw new Error('Failed to complete mindfulness session');
    }
  }

  /**
   * Get recent sessions (last 7 days)
   */
  static async getRecentSessions(): Promise<MindfulnessSession[]> {
    try {
      const response = await this.getSessions({ limit: 20 });
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

      return response.sessions.filter(session => 
        new Date(session.created_at) > sevenDaysAgo
      );
    } catch (error) {
      console.error('Error fetching recent sessions:', error);
      throw new Error('Failed to fetch recent sessions');
    }
  }

  /**
   * Get sessions by type
   */
  static async getSessionsByType(sessionType: string): Promise<MindfulnessSession[]> {
    try {
      const response = await this.getSessions({ session_type: sessionType });
      return response.sessions;
    } catch (error) {
      console.error('Error fetching sessions by type:', error);
      throw new Error('Failed to fetch sessions by type');
    }
  }

  /**
   * Calculate session effectiveness trend
   */
  static calculateEffectivenessTrend(sessions: MindfulnessSession[]): number | null {
    const ratingsWithDates = sessions
      .filter(session => session.effectiveness_rating && session.completed_at)
      .sort((a, b) => new Date(a.completed_at!).getTime() - new Date(b.completed_at!).getTime());

    if (ratingsWithDates.length < 2) return null;

    const firstHalf = ratingsWithDates.slice(0, Math.floor(ratingsWithDates.length / 2));
    const secondHalf = ratingsWithDates.slice(Math.floor(ratingsWithDates.length / 2));

    const firstHalfAvg = firstHalf.reduce((sum, session) => sum + session.effectiveness_rating!, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, session) => sum + session.effectiveness_rating!, 0) / secondHalf.length;

    return secondHalfAvg - firstHalfAvg;
  }

  /**
   * Get personalized session recommendations based on user's history
   */
  static async getPersonalizedRecommendations(): Promise<SessionTemplate[]> {
    try {
      const [templatesResponse, analyticsResponse] = await Promise.all([
        this.getTemplates(),
        this.getAnalytics(30)
      ]);

      const templates = templatesResponse.templates;
      const analytics = analyticsResponse.analytics;

      // Simple recommendation logic based on session type usage
      const recommendations: SessionTemplate[] = [];
      
      // If user has no sessions, recommend beginners' options
      if (analytics.total_sessions === 0) {
        recommendations.push(
          templates.breathing[0], // 4-7-8 Breathing
          templates.meditation[2], // Quick Centering
        );
      } else {
        // Recommend less used session types
        const sessionTypeCounts = analytics.session_types;
        const leastUsedTypes = Object.entries(sessionTypeCounts)
          .sort(([,a], [,b]) => a - b)
          .slice(0, 2)
          .map(([type]) => type);

        for (const type of leastUsedTypes) {
          if (templates[type as keyof SessionTemplates]) {
            recommendations.push(templates[type as keyof SessionTemplates][0]);
          }
        }
      }

      return recommendations.slice(0, 3); // Return top 3 recommendations
    } catch (error) {
      console.error('Error getting personalized recommendations:', error);
      throw new Error('Failed to get personalized recommendations');
    }
  }
} 
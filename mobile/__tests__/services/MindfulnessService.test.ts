import { MindfulnessService } from '../../src/services/MindfulnessService';
import { ApiClient } from '../../src/services/ApiClient';

// Mock ApiClient
jest.mock('../../src/services/ApiClient');
const mockApiClient = ApiClient as jest.Mocked<typeof ApiClient>;

describe('MindfulnessService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getSessions', () => {
    it('should fetch sessions successfully without filters', async () => {
      const mockResponse = {
        sessions: [
          {
            id: 1,
            session_type: 'breathing' as const,
            title: 'Test Session',
            duration_minutes: 10,
            completed: false,
            created_at: '2024-01-01T00:00:00Z'
          }
        ],
        total: 1
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getSessions();

      expect(mockApiClient.get).toHaveBeenCalledWith('/mindfulness/sessions');
      expect(result).toEqual(mockResponse);
    });

    it('should fetch sessions with filters', async () => {
      const mockResponse = {
        sessions: [
          {
            id: 1,
            session_type: 'meditation' as const,
            title: 'Meditation Session',
            duration_minutes: 15,
            completed: true,
            created_at: '2024-01-01T00:00:00Z'
          }
        ],
        total: 1
      };

      const options = {
        session_type: 'meditation',
        completed: true,
        limit: 10,
        offset: 0
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getSessions(options);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/mindfulness/sessions?session_type=meditation&completed=true&limit=10&offset=0'
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Network error'));

      await expect(MindfulnessService.getSessions()).rejects.toThrow(
        'Failed to fetch mindfulness sessions'
      );
    });
  });

  describe('createSession', () => {
    it('should create a session successfully', async () => {
      const sessionData = {
        session_type: 'breathing' as const,
        title: 'Test Breathing',
        description: 'A test session',
        duration_minutes: 10,
        mood_before: 5,
        stress_before: 7
      };

      const mockResponse = {
        message: 'Mindfulness session created successfully',
        session: {
          id: 1,
          ...sessionData,
          completed: false,
          created_at: '2024-01-01T00:00:00Z'
        }
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.createSession(sessionData);

      expect(mockApiClient.post).toHaveBeenCalledWith('/mindfulness/sessions', sessionData);
      expect(result).toEqual(mockResponse);
    });

    it('should handle creation errors', async () => {
      const sessionData = {
        session_type: 'breathing' as const,
        title: 'Test Session',
        duration_minutes: 10
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Validation error'));

      await expect(MindfulnessService.createSession(sessionData)).rejects.toThrow(
        'Failed to create mindfulness session'
      );
    });
  });

  describe('getSession', () => {
    it('should fetch a specific session successfully', async () => {
      const mockResponse = {
        session: {
          id: 1,
          session_type: 'meditation' as const,
          title: 'Test Meditation',
          duration_minutes: 15,
          completed: false,
          created_at: '2024-01-01T00:00:00Z'
        }
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getSession(1);

      expect(mockApiClient.get).toHaveBeenCalledWith('/mindfulness/sessions/1');
      expect(result).toEqual(mockResponse);
    });

    it('should handle session not found', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Session not found'));

      await expect(MindfulnessService.getSession(999)).rejects.toThrow(
        'Failed to fetch mindfulness session'
      );
    });
  });

  describe('updateSession', () => {
    it('should update a session successfully', async () => {
      const updateData = {
        completed: true,
        completed_duration_minutes: 8,
        mood_after: 7,
        stress_after: 4,
        effectiveness_rating: 8,
        notes: 'Great session!'
      };

      const mockResponse = {
        message: 'Session updated successfully',
        session: {
          id: 1,
          session_type: 'breathing' as const,
          title: 'Test Session',
          duration_minutes: 10,
          ...updateData,
          created_at: '2024-01-01T00:00:00Z',
          completed_at: '2024-01-01T00:10:00Z'
        }
      };

      mockApiClient.put.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.updateSession(1, updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith('/mindfulness/sessions/1', updateData);
      expect(result).toEqual(mockResponse);
    });

    it('should handle update errors', async () => {
      const updateData = { completed: true };

      mockApiClient.put.mockRejectedValueOnce(new Error('Update failed'));

      await expect(MindfulnessService.updateSession(1, updateData)).rejects.toThrow(
        'Failed to update mindfulness session'
      );
    });
  });

  describe('deleteSession', () => {
    it('should delete a session successfully', async () => {
      const mockResponse = {
        message: 'Session deleted successfully'
      };

      mockApiClient.delete.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.deleteSession(1);

      expect(mockApiClient.delete).toHaveBeenCalledWith('/mindfulness/sessions/1');
      expect(result).toEqual(mockResponse);
    });

    it('should handle deletion errors', async () => {
      mockApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(MindfulnessService.deleteSession(1)).rejects.toThrow(
        'Failed to delete mindfulness session'
      );
    });
  });

  describe('getTemplates', () => {
    it('should fetch templates successfully', async () => {
      const mockResponse = {
        templates: {
          breathing: [
            {
              title: '4-7-8 Breathing',
              description: 'A calming breathing technique',
              duration_minutes: 5,
              instructions: 'Inhale for 4, hold for 7, exhale for 8'
            }
          ],
          meditation: [
            {
              title: 'Mindfulness Meditation',
              description: 'Focus on the present moment',
              duration_minutes: 15,
              instructions: 'Sit comfortably and focus on your breath'
            }
          ],
          body_scan: [],
          progressive_relaxation: []
        }
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getTemplates();

      expect(mockApiClient.get).toHaveBeenCalledWith('/mindfulness/templates');
      expect(result).toEqual(mockResponse);
    });

    it('should handle template fetch errors', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Fetch failed'));

      await expect(MindfulnessService.getTemplates()).rejects.toThrow(
        'Failed to fetch session templates'
      );
    });
  });

  describe('getAnalytics', () => {
    it('should fetch analytics successfully without days parameter', async () => {
      const mockResponse = {
        analytics: {
          period_days: 30,
          total_sessions: 5,
          completed_sessions: 4,
          completion_rate: 0.8,
          total_minutes: 60,
          average_effectiveness: 8.5,
          average_mood_improvement: 2.0,
          average_stress_reduction: 3.0,
          session_types: { breathing: 2, meditation: 3 },
          streak_days: 3
        }
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getAnalytics();

      expect(mockApiClient.get).toHaveBeenCalledWith('/mindfulness/analytics');
      expect(result).toEqual(mockResponse);
    });

    it('should fetch analytics with custom days parameter', async () => {
      const mockResponse = {
        analytics: {
          period_days: 7,
          total_sessions: 2,
          completed_sessions: 2,
          completion_rate: 1.0,
          total_minutes: 20,
          session_types: { breathing: 1, meditation: 1 },
          streak_days: 2
        }
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getAnalytics(7);

      expect(mockApiClient.get).toHaveBeenCalledWith('/mindfulness/analytics?days=7');
      expect(result).toEqual(mockResponse);
    });

    it('should handle analytics fetch errors', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Analytics failed'));

      await expect(MindfulnessService.getAnalytics()).rejects.toThrow(
        'Failed to fetch mindfulness analytics'
      );
    });
  });

  describe('startSession', () => {
    it('should start a session successfully', async () => {
      const template = {
        title: 'Test Template',
        description: 'A test template',
        duration_minutes: 10,
        instructions: 'Follow the instructions'
      };

      const preSessionData = {
        mood_before: 5,
        stress_before: 7
      };

      const mockResponse = {
        message: 'Mindfulness session created successfully',
        session: {
          id: 1,
          session_type: 'meditation' as const,
          title: 'Test Template',
          description: 'A test template',
          duration_minutes: 10,
          mood_before: 5,
          stress_before: 7,
          completed: false,
          created_at: '2024-01-01T00:00:00Z'
        }
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.startSession(template, preSessionData);

      expect(mockApiClient.post).toHaveBeenCalledWith('/mindfulness/sessions', {
        session_type: 'meditation',
        title: 'Test Template',
        description: 'A test template',
        duration_minutes: 10,
        mood_before: 5,
        stress_before: 7
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle start session errors', async () => {
      const template = {
        title: 'Test Template',
        description: 'A test template',
        duration_minutes: 10,
        instructions: 'Follow the instructions'
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Start failed'));

      await expect(MindfulnessService.startSession(template, {})).rejects.toThrow(
        'Failed to start mindfulness session'
      );
    });
  });

  describe('completeSession', () => {
    it('should complete a session successfully', async () => {
      const completionData = {
        completed_duration_minutes: 8,
        mood_after: 7,
        stress_after: 4,
        effectiveness_rating: 8,
        notes: 'Great session!'
      };

      const mockResponse = {
        message: 'Session updated successfully',
        session: {
          id: 1,
          session_type: 'breathing' as const,
          title: 'Test Session',
          duration_minutes: 10,
          completed: true,
          ...completionData,
          created_at: '2024-01-01T00:00:00Z',
          completed_at: '2024-01-01T00:10:00Z'
        }
      };

      mockApiClient.put.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.completeSession(1, completionData);

      expect(mockApiClient.put).toHaveBeenCalledWith('/mindfulness/sessions/1', {
        completed: true,
        ...completionData
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle complete session errors', async () => {
      const completionData = {
        completed_duration_minutes: 8
      };

      mockApiClient.put.mockRejectedValueOnce(new Error('Complete failed'));

      await expect(MindfulnessService.completeSession(1, completionData)).rejects.toThrow(
        'Failed to complete mindfulness session'
      );
    });
  });

  describe('getRecentSessions', () => {
    it('should fetch recent sessions successfully', async () => {
      const mockSessions = [
        {
          id: 1,
          session_type: 'breathing' as const,
          title: 'Recent Session 1',
          duration_minutes: 10,
          completed: true,
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          session_type: 'meditation' as const,
          title: 'Recent Session 2',
          duration_minutes: 15,
          completed: false,
          created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() // 2 days ago
        }
      ];

      const mockResponse = {
        sessions: mockSessions,
        total: 2
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getRecentSessions();

      expect(mockApiClient.get).toHaveBeenCalledWith('/mindfulness/sessions?limit=20');
      expect(result).toHaveLength(2);
      expect(result[0].title).toBe('Recent Session 1');
    });

    it('should filter out sessions older than 7 days', async () => {
      const oldSession = {
        id: 1,
        session_type: 'breathing' as const,
        title: 'Old Session',
        duration_minutes: 10,
        completed: true,
        created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString() // 10 days ago
      };

      const recentSession = {
        id: 2,
        session_type: 'meditation' as const,
        title: 'Recent Session',
        duration_minutes: 15,
        completed: false,
        created_at: new Date().toISOString()
      };

      const mockResponse = {
        sessions: [oldSession, recentSession],
        total: 2
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getRecentSessions();

      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('Recent Session');
    });
  });

  describe('getSessionsByType', () => {
    it('should fetch sessions by type successfully', async () => {
      const mockResponse = {
        sessions: [
          {
            id: 1,
            session_type: 'breathing' as const,
            title: 'Breathing Session 1',
            duration_minutes: 5,
            completed: true,
            created_at: '2024-01-01T00:00:00Z'
          }
        ],
        total: 1
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await MindfulnessService.getSessionsByType('breathing');

      expect(mockApiClient.get).toHaveBeenCalledWith('/mindfulness/sessions?session_type=breathing');
      expect(result).toEqual(mockResponse.sessions);
    });
  });

  describe('calculateEffectivenessTrend', () => {
    it('should calculate positive trend correctly', () => {
      const sessions = [
        {
          id: 1,
          session_type: 'breathing' as const,
          title: 'Session 1',
          duration_minutes: 10,
          completed: true,
          effectiveness_rating: 6,
          completed_at: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          session_type: 'breathing' as const,
          title: 'Session 2',
          duration_minutes: 10,
          completed: true,
          effectiveness_rating: 7,
          completed_at: '2024-01-02T00:00:00Z',
          created_at: '2024-01-02T00:00:00Z'
        },
        {
          id: 3,
          session_type: 'breathing' as const,
          title: 'Session 3',
          duration_minutes: 10,
          completed: true,
          effectiveness_rating: 8,
          completed_at: '2024-01-03T00:00:00Z',
          created_at: '2024-01-03T00:00:00Z'
        },
        {
          id: 4,
          session_type: 'breathing' as const,
          title: 'Session 4',
          duration_minutes: 10,
          completed: true,
          effectiveness_rating: 9,
          completed_at: '2024-01-04T00:00:00Z',
          created_at: '2024-01-04T00:00:00Z'
        }
      ];

      const trend = MindfulnessService.calculateEffectivenessTrend(sessions);

      expect(trend).toBe(1.5); // ((8+9)/2) - ((6+7)/2) = 8.5 - 6.5 = 2
    });

    it('should return null for insufficient data', () => {
      const sessions = [
        {
          id: 1,
          session_type: 'breathing' as const,
          title: 'Session 1',
          duration_minutes: 10,
          completed: true,
          effectiveness_rating: 6,
          completed_at: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z'
        }
      ];

      const trend = MindfulnessService.calculateEffectivenessTrend(sessions);

      expect(trend).toBeNull();
    });

    it('should handle sessions without ratings', () => {
      const sessions = [
        {
          id: 1,
          session_type: 'breathing' as const,
          title: 'Session 1',
          duration_minutes: 10,
          completed: true,
          created_at: '2024-01-01T00:00:00Z'
        }
      ];

      const trend = MindfulnessService.calculateEffectivenessTrend(sessions);

      expect(trend).toBeNull();
    });
  });

  describe('getPersonalizedRecommendations', () => {
    it('should return beginner recommendations for new users', async () => {
      const mockTemplatesResponse = {
        templates: {
          breathing: [
            {
              title: '4-7-8 Breathing',
              description: 'A calming technique',
              duration_minutes: 5,
              instructions: 'Inhale 4, hold 7, exhale 8'
            }
          ],
          meditation: [
            {
              title: 'Basic Meditation',
              description: 'Simple meditation',
              duration_minutes: 10,
              instructions: 'Focus on breath'
            },
            {
              title: 'Advanced Meditation',
              description: 'Advanced practice',
              duration_minutes: 20,
              instructions: 'Deep focus'
            },
            {
              title: 'Quick Centering',
              description: 'Quick practice',
              duration_minutes: 5,
              instructions: 'Quick centering'
            }
          ],
          body_scan: [],
          progressive_relaxation: []
        }
      };

      const mockAnalyticsResponse = {
        analytics: {
          period_days: 30,
          total_sessions: 0,
          completed_sessions: 0,
          completion_rate: 0,
          total_minutes: 0,
          session_types: {},
          streak_days: 0
        }
      };

      mockApiClient.get
        .mockResolvedValueOnce(mockTemplatesResponse)
        .mockResolvedValueOnce(mockAnalyticsResponse);

      const result = await MindfulnessService.getPersonalizedRecommendations();

      expect(result).toHaveLength(2);
      expect(result[0].title).toBe('4-7-8 Breathing');
      expect(result[1].title).toBe('Quick Centering');
    });

    it('should recommend least used session types for experienced users', async () => {
      const mockTemplatesResponse = {
        templates: {
          breathing: [
            {
              title: '4-7-8 Breathing',
              description: 'A calming technique',
              duration_minutes: 5,
              instructions: 'Inhale 4, hold 7, exhale 8'
            }
          ],
          meditation: [
            {
              title: 'Basic Meditation',
              description: 'Simple meditation',
              duration_minutes: 10,
              instructions: 'Focus on breath'
            }
          ],
          body_scan: [
            {
              title: 'Full Body Scan',
              description: 'Scan your body',
              duration_minutes: 20,
              instructions: 'Scan from head to toe'
            }
          ],
          progressive_relaxation: [
            {
              title: 'Progressive Relaxation',
              description: 'Relax muscles',
              duration_minutes: 15,
              instructions: 'Tense and release'
            }
          ]
        }
      };

      const mockAnalyticsResponse = {
        analytics: {
          period_days: 30,
          total_sessions: 10,
          completed_sessions: 8,
          completion_rate: 0.8,
          total_minutes: 120,
          session_types: {
            breathing: 5,
            meditation: 3,
            body_scan: 1,
            progressive_relaxation: 1
          },
          streak_days: 3
        }
      };

      mockApiClient.get
        .mockResolvedValueOnce(mockTemplatesResponse)
        .mockResolvedValueOnce(mockAnalyticsResponse);

      const result = await MindfulnessService.getPersonalizedRecommendations();

      expect(result).toHaveLength(2);
      // Should recommend least used types (body_scan and progressive_relaxation)
      expect(result[0].title).toBe('Full Body Scan');
      expect(result[1].title).toBe('Progressive Relaxation');
    });

    it('should handle recommendation errors', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Recommendations failed'));

      await expect(MindfulnessService.getPersonalizedRecommendations()).rejects.toThrow(
        'Failed to get personalized recommendations'
      );
    });
  });
}); 
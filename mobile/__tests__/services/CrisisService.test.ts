import { CrisisService } from '../../src/services/CrisisService';
import { ApiClient } from '../../src/services/ApiClient';

// Mock ApiClient
jest.mock('../../src/services/ApiClient');
const mockApiClient = ApiClient as jest.Mocked<typeof ApiClient>;

describe('CrisisService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('analyzeContent', () => {
    it('should analyze content for crisis indicators successfully', async () => {
      const mockResponse = {
        risk_level: 'medium',
        confidence: 0.75,
        detected_factors: ['hopelessness'],
        recommended_interventions: ['Contact crisis counselor', 'Safety planning'],
        safety_resources: [],
        escalation_needed: false,
        assessment_timestamp: '2024-01-01T00:00:00Z'
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.analyzeContent('I feel hopeless');

      expect(mockApiClient.post).toHaveBeenCalledWith('/crisis/analyze', {
        content: 'I feel hopeless'
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle analysis errors', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Analysis failed'));

      await expect(CrisisService.analyzeContent('test content')).rejects.toThrow(
        'Failed to analyze content for crisis indicators'
      );
    });
  });

  describe('assessCrisisRisk', () => {
    it('should assess crisis risk with context successfully', async () => {
      const mockResponse = {
        data: {
          risk_assessment: {
            risk_level: 'high' as const,
            confidence: 0.85,
            detected_factors: ['suicidal_ideation'],
            recommended_interventions: ['Immediate professional help'],
            safety_resources: [],
            escalation_needed: true,
            assessment_timestamp: '2024-01-01T00:00:00Z'
          }
        }
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.assessCrisisRisk(
        'I want to end it all',
        'chat',
        { mood_score: 2 }
      );

      expect(mockApiClient.post).toHaveBeenCalledWith('/crisis/assess', {
        content: 'I want to end it all',
        source: 'chat',
        context: { mood_score: 2 }
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle risk assessment errors', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Assessment failed'));

      await expect(CrisisService.assessCrisisRisk('test')).rejects.toThrow(
        'Failed to assess crisis risk'
      );
    });
  });

  describe('getEmergencyContacts', () => {
    it('should fetch emergency contacts successfully', async () => {
      const mockResponse = {
        contacts: [
          {
            id: 'ec_001',
            name: 'National Suicide Prevention Lifeline',
            phone: '988',
            relationship: 'crisis_hotline',
            priority: 1,
            is_active: true
          }
        ]
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.getEmergencyContacts();

      expect(mockApiClient.get).toHaveBeenCalledWith('/crisis/emergency-contacts');
      expect(result).toEqual(mockResponse);
    });

    it('should handle emergency contacts fetch errors', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Fetch failed'));

      await expect(CrisisService.getEmergencyContacts()).rejects.toThrow(
        'Failed to fetch emergency contacts'
      );
    });
  });

  describe('getSafetyResources', () => {
    it('should fetch safety resources successfully', async () => {
      const mockResponse = {
        resources: [
          {
            id: 'sr_001',
            name: 'Crisis Text Line',
            type: 'text' as const,
            contact: '741741',
            description: 'Text-based crisis support',
            availability: '24/7',
            is_emergency: true
          }
        ]
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.getSafetyResources();

      expect(mockApiClient.get).toHaveBeenCalledWith('/crisis/resources');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('createSafetyPlan', () => {
    it('should create safety plan successfully', async () => {
      const planData = {
        warning_signs: ['Feeling hopeless'],
        coping_strategies: ['Call a friend'],
        support_people: ['John Doe'],
        professional_contacts: ['Dr. Smith'],
        environment_safety: ['Remove harmful items'],
        reasons_to_live: ['Family']
      };

      const mockResponse = {
        data: {
          plan_id: 'sp_123',
          created_at: '2024-01-01T00:00:00Z'
        }
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.createSafetyPlan(planData);

      expect(mockApiClient.post).toHaveBeenCalledWith('/crisis/safety-plan', planData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getRiskFactors', () => {
    it('should fetch risk factors successfully', async () => {
      const mockResponse = {
        data: {
          risk_factors: [
            {
              name: 'suicidal_ideation',
              display_name: 'Suicidal Ideation',
              description: 'Thoughts of suicide',
              severity: 'high' as const,
              warning_signs: ['Talking about wanting to die']
            }
          ]
        }
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.getRiskFactors();

      expect(mockApiClient.get).toHaveBeenCalledWith('/crisis/risk-factors');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('containsCrisisKeywords', () => {
    it('should detect crisis keywords', () => {
      expect(CrisisService.containsCrisisKeywords('I want to kill myself')).toBe(true);
      expect(CrisisService.containsCrisisKeywords('I feel hopeless')).toBe(true);
      expect(CrisisService.containsCrisisKeywords('I am sad')).toBe(false);
      expect(CrisisService.containsCrisisKeywords('Everything is fine')).toBe(false);
    });

    it('should be case insensitive', () => {
      expect(CrisisService.containsCrisisKeywords('I WANT TO DIE')).toBe(true);
      expect(CrisisService.containsCrisisKeywords('Suicide is on my mind')).toBe(true);
    });
  });

  describe('getInterventionMessage', () => {
    it('should return appropriate messages for different risk levels', () => {
      expect(CrisisService.getInterventionMessage('critical')).toContain('crisis situation');
      expect(CrisisService.getInterventionMessage('high')).toContain('concerned about your wellbeing');
      expect(CrisisService.getInterventionMessage('medium')).toContain('might be struggling');
      expect(CrisisService.getInterventionMessage('low')).toContain('here to support');
      expect(CrisisService.getInterventionMessage('none')).toContain('help is always available');
    });
  });

  describe('formatPhoneNumber', () => {
    it('should format different phone number types correctly', () => {
      expect(CrisisService.formatPhoneNumber('988')).toBe('988');
      expect(CrisisService.formatPhoneNumber('741741')).toBe('741741');
      expect(CrisisService.formatPhoneNumber('5551234567')).toBe('(555) 123-4567');
      expect(CrisisService.formatPhoneNumber('15551234567')).toBe('+1 (555) 123-4567');
      expect(CrisisService.formatPhoneNumber('invalid')).toBe('invalid');
    });

    it('should handle phone numbers with formatting characters', () => {
      expect(CrisisService.formatPhoneNumber('(555) 123-4567')).toBe('(555) 123-4567');
      expect(CrisisService.formatPhoneNumber('+1-555-123-4567')).toBe('+1 (555) 123-4567');
    });
  });

  describe('escalateCrisis', () => {
    it('should escalate crisis successfully', async () => {
      const mockResponse = {
        data: {
          escalation_id: 'esc_123',
          actions_taken: ['Professional notified'],
          timestamp: '2024-01-01T00:00:00Z'
        }
      };

      mockApiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.escalateCrisis(
        'high',
        'User expressed suicidal thoughts',
        'professional',
        true,
        { location: 'City, State' }
      );

      expect(mockApiClient.post).toHaveBeenCalledWith('/crisis/escalate', {
        crisis_level: 'high',
        trigger_content: 'User expressed suicidal thoughts',
        escalation_type: 'professional',
        user_consent: true,
        additional_info: { location: 'City, State' }
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getCrisisHistory', () => {
    it('should fetch crisis history successfully', async () => {
      const mockResponse = {
        data: {
          events: [
            {
              id: 'ce_001',
              crisis_level: 'medium',
              trigger_source: 'chat',
              created_at: '2024-01-01T00:00:00Z'
            }
          ]
        }
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await CrisisService.getCrisisHistory(7);

      expect(mockApiClient.get).toHaveBeenCalledWith('/crisis/history?days=7');
      expect(result).toEqual(mockResponse);
    });

    it('should use default days parameter', async () => {
      const mockResponse = { data: { events: [] } };
      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      await CrisisService.getCrisisHistory();

      expect(mockApiClient.get).toHaveBeenCalledWith('/crisis/history?days=30');
    });
  });
}); 
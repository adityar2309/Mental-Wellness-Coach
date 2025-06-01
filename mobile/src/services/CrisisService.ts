import { ApiClient } from './ApiClient';

export interface CrisisRiskAssessment {
  risk_level: 'none' | 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  detected_factors: string[];
  recommended_interventions: string[];
  safety_resources: SafetyResource[];
  escalation_needed: boolean;
  assessment_timestamp: string;
}

export interface CrisisAnalysisResponse {
  risk_level: string;
  confidence: number;
  detected_factors: string[];
  recommended_interventions: string[];
  safety_resources: SafetyResource[];
  escalation_needed: boolean;
  assessment_timestamp: string;
}

export interface SafetyResource {
  id: string;
  name: string;
  type: 'hotline' | 'text' | 'chat' | 'website' | 'app';
  contact: string;
  description: string;
  availability: string;
  is_emergency: boolean;
}

export interface EmergencyContact {
  id: string;
  name: string;
  phone: string;
  relationship: string;
  priority: number;
  is_active: boolean;
}

export interface RiskFactor {
  name: string;
  display_name: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  warning_signs: string[];
}

export interface SafetyPlan {
  plan_id: string;
  warning_signs: string[];
  coping_strategies: string[];
  support_people: string[];
  professional_contacts: string[];
  environment_safety: string[];
  reasons_to_live: string[];
  created_at: string;
}

export interface CreateSafetyPlanData {
  warning_signs: string[];
  coping_strategies: string[];
  support_people: string[];
  professional_contacts?: string[];
  environment_safety?: string[];
  reasons_to_live?: string[];
}

export class CrisisService {
  /**
   * Analyze content for crisis indicators
   */
  static async analyzeContent(content: string): Promise<CrisisAnalysisResponse> {
    try {
      const response = await ApiClient.post<CrisisAnalysisResponse>('/crisis/analyze', {
        content
      });
      return response;
    } catch (error) {
      console.error('Error analyzing crisis content:', error);
      throw new Error('Failed to analyze content for crisis indicators');
    }
  }

  /**
   * Assess crisis risk with additional context
   */
  static async assessCrisisRisk(
    content: string,
    source: string = 'chat',
    context: Record<string, any> = {}
  ): Promise<{ data: { risk_assessment: CrisisRiskAssessment } }> {
    try {
      const response = await ApiClient.post<{ data: { risk_assessment: CrisisRiskAssessment } }>('/crisis/assess', {
        content,
        source,
        context
      });
      return response;
    } catch (error) {
      console.error('Error assessing crisis risk:', error);
      throw new Error('Failed to assess crisis risk');
    }
  }

  /**
   * Get safety resources
   */
  static async getSafetyResources(): Promise<{ resources: SafetyResource[] }> {
    try {
      const response = await ApiClient.get<{ resources: SafetyResource[] }>('/crisis/resources');
      return response;
    } catch (error) {
      console.error('Error fetching safety resources:', error);
      throw new Error('Failed to fetch safety resources');
    }
  }

  /**
   * Get emergency contacts
   */
  static async getEmergencyContacts(): Promise<{ contacts: EmergencyContact[] }> {
    try {
      const response = await ApiClient.get<{ contacts: EmergencyContact[] }>('/crisis/emergency-contacts');
      return response;
    } catch (error) {
      console.error('Error fetching emergency contacts:', error);
      throw new Error('Failed to fetch emergency contacts');
    }
  }

  /**
   * Get risk factors information
   */
  static async getRiskFactors(): Promise<{ data: { risk_factors: RiskFactor[] } }> {
    try {
      const response = await ApiClient.get<{ data: { risk_factors: RiskFactor[] } }>('/crisis/risk-factors');
      return response;
    } catch (error) {
      console.error('Error fetching risk factors:', error);
      throw new Error('Failed to fetch risk factors');
    }
  }

  /**
   * Create a safety plan
   */
  static async createSafetyPlan(planData: CreateSafetyPlanData): Promise<{ data: { plan_id: string; created_at: string } }> {
    try {
      const response = await ApiClient.post<{ data: { plan_id: string; created_at: string } }>('/crisis/safety-plan', planData);
      return response;
    } catch (error) {
      console.error('Error creating safety plan:', error);
      throw new Error('Failed to create safety plan');
    }
  }

  /**
   * Escalate a crisis situation
   */
  static async escalateCrisis(
    crisisLevel: string,
    triggerContent: string,
    escalationType: string = 'professional',
    userConsent: boolean = false,
    additionalInfo: Record<string, any> = {}
  ): Promise<{ data: any }> {
    try {
      const response = await ApiClient.post<{ data: any }>('/crisis/escalate', {
        crisis_level: crisisLevel,
        trigger_content: triggerContent,
        escalation_type: escalationType,
        user_consent: userConsent,
        additional_info: additionalInfo
      });
      return response;
    } catch (error) {
      console.error('Error escalating crisis:', error);
      throw new Error('Failed to escalate crisis');
    }
  }

  /**
   * Get crisis history
   */
  static async getCrisisHistory(days: number = 30): Promise<{ data: { events: any[] } }> {
    try {
      const response = await ApiClient.get<{ data: { events: any[] } }>(`/crisis/history?days=${days}`);
      return response;
    } catch (error) {
      console.error('Error fetching crisis history:', error);
      throw new Error('Failed to fetch crisis history');
    }
  }

  /**
   * Check if content contains crisis indicators (helper method)
   */
  static containsCrisisKeywords(content: string): boolean {
    const crisisKeywords = [
      'suicide', 'kill myself', 'end it all', 'want to die', 'hurt myself',
      'self harm', 'not worth living', 'hopeless', 'no point in living',
      'overdose', 'cutting', 'worthless', 'better off dead'
    ];

    const normalizedContent = content.toLowerCase();
    return crisisKeywords.some(keyword => normalizedContent.includes(keyword));
  }

  /**
   * Get appropriate intervention message based on risk level
   */
  static getInterventionMessage(riskLevel: string): string {
    switch (riskLevel) {
      case 'critical':
        return 'This is a crisis situation. Please reach out to emergency services (911) or a crisis hotline immediately. You are not alone.';
      case 'high':
        return 'I\'m concerned about your wellbeing. Please consider reaching out to a crisis counselor or trusted person. Help is available.';
      case 'medium':
        return 'I notice you might be struggling. Would you like to explore some coping strategies or talk to someone who can help?';
      case 'low':
        return 'I\'m here to support you. Would you like to talk about what\'s bothering you or learn some coping techniques?';
      default:
        return 'If you\'re ever feeling overwhelmed, remember that help is always available. You don\'t have to face difficulties alone.';
    }
  }

  /**
   * Format phone number for calling
   */
  static formatPhoneNumber(phone: string): string {
    // Remove all non-numeric characters
    const cleanPhone = phone.replace(/\D/g, '');
    
    // Format based on length
    if (cleanPhone.length === 3) {
      return cleanPhone; // For 988, 911, etc.
    } else if (cleanPhone.length === 6) {
      return cleanPhone; // For 741741, etc.
    } else if (cleanPhone.length === 10) {
      return `(${cleanPhone.slice(0, 3)}) ${cleanPhone.slice(3, 6)}-${cleanPhone.slice(6)}`;
    } else if (cleanPhone.length === 11 && cleanPhone[0] === '1') {
      return `+1 (${cleanPhone.slice(1, 4)}) ${cleanPhone.slice(4, 7)}-${cleanPhone.slice(7)}`;
    }
    
    return phone; // Return original if format not recognized
  }
} 
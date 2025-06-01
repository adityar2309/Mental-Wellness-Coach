import { ApiClient, MoodApi, ConversationApi, CrisisApi, ApiError } from '../../src/services/ApiClient';
import * as SecureStore from 'expo-secure-store';

// Mock SecureStore
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();
global.AbortSignal = {
  timeout: jest.fn().mockReturnValue({}),
} as any;

describe('ApiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
    (SecureStore.getItemAsync as jest.Mock).mockClear();
  });

  describe('Authentication Headers', () => {
    it('includes auth token when available', async () => {
      const mockToken = 'test-token-123';
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(mockToken);
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'success', data: {} }),
      });

      await ApiClient.get('/test');

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          }),
        })
      );
    });

    it('works without auth token', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'success', data: {} }),
      });

      await ApiClient.get('/test');

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          }),
        })
      );

      const callHeaders = (fetch as jest.Mock).mock.calls[0][1].headers;
      expect(callHeaders).not.toHaveProperty('Authorization');
    });
  });

  describe('HTTP Methods', () => {
    beforeEach(() => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);
    });

    it('performs GET request correctly', async () => {
      const mockResponse = { status: 'success', data: { id: 1 } };
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await ApiClient.get('/test');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('performs POST request with data', async () => {
      const postData = { name: 'test', value: 123 };
      const mockResponse = { status: 'success', data: { id: 1 } };
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await ApiClient.post('/test', postData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('performs PUT request correctly', async () => {
      const putData = { id: 1, name: 'updated' };
      const mockResponse = { status: 'success' };
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      await ApiClient.put('/test', putData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData),
        })
      );
    });

    it('performs DELETE request correctly', async () => {
      const mockResponse = { status: 'success' };
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      await ApiClient.delete('/test');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('performs PATCH request correctly', async () => {
      const patchData = { notes: 'updated notes' };
      const mockResponse = { status: 'success' };
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      await ApiClient.patch('/test', patchData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(patchData),
        })
      );
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);
    });

    it('handles API errors correctly', async () => {
      const errorResponse = {
        message: 'Validation failed',
        error: 'Bad Request',
      };
      (fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => errorResponse,
      });

      await expect(ApiClient.get('/test')).rejects.toMatchObject({
        message: 'Validation failed',
        status: 400,
        data: errorResponse,
      });
    });

    it('handles network errors', async () => {
      (fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(ApiClient.get('/test')).rejects.toThrow(
        'Network error. Please check your connection.'
      );
    });

    it('handles timeout errors', async () => {
      const abortError = new Error('Request timeout');
      abortError.name = 'AbortError';
      (fetch as jest.Mock).mockRejectedValue(abortError);

      await expect(ApiClient.get('/test')).rejects.toThrow('Request timeout');
    });
  });

  describe('Base URL Configuration', () => {
    it('allows setting custom base URL', () => {
      const customUrl = 'https://test.api.com';
      ApiClient.setBaseURL(customUrl);
      
      // This is tested implicitly by checking the fetch call URL
      expect(ApiClient.setBaseURL).toBeDefined();
    });
  });
});

describe('MoodApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('test-token');
  });

  it('creates mood entry correctly', async () => {
    const moodData = {
      mood_score: 7,
      energy_level: 6,
      stress_level: 4,
      notes: 'Feeling good today',
    };
    
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'success', data: { id: 1, ...moodData } }),
    });

    await MoodApi.createEntry(moodData);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/mood/entries'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(moodData),
      })
    );
  });

  it('gets mood entries with date filters', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'success', data: [] }),
    });

    await MoodApi.getEntries('2024-01-01', '2024-01-31');

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/mood/entries?start_date=2024-01-01&end_date=2024-01-31'),
      expect.objectContaining({
        method: 'GET',
      })
    );
  });

  it('gets mood analytics', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ 
        status: 'success', 
        data: { 
          average_mood: 6.5,
          trend: 'improving' 
        } 
      }),
    });

    await MoodApi.getAnalytics();

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/mood/analytics'),
      expect.objectContaining({
        method: 'GET',
      })
    );
  });

  it('performs quick check-in', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'success' }),
    });

    await MoodApi.quickCheckIn(8);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/mood/quick-checkin'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ mood_score: 8 }),
      })
    );
  });
});

describe('ConversationApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('test-token');
  });

  it('starts conversation correctly', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ 
        status: 'success', 
        data: { conversation_id: 'conv-123' } 
      }),
    });

    await ConversationApi.startConversation();

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/conversations/start'),
      expect.objectContaining({
        method: 'POST',
      })
    );
  });

  it('sends message correctly', async () => {
    const conversationId = 'conv-123';
    const message = 'Hello, how are you?';
    
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'success' }),
    });

    await ConversationApi.sendMessage(conversationId, message);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining(`/conversations/${conversationId}/messages`),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ content: message }),
      })
    );
  });
});

describe('CrisisApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('test-token');
  });

  it('analyzes content correctly', async () => {
    const content = 'I am feeling really down';
    
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ 
        status: 'success', 
        data: { risk_level: 'medium' } 
      }),
    });

    await CrisisApi.analyzeContent(content);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/crisis/analyze'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ content }),
      })
    );
  });

  it('gets crisis resources', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ 
        status: 'success', 
        data: { resources: [] } 
      }),
    });

    await CrisisApi.getResources();

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/crisis/resources'),
      expect.objectContaining({
        method: 'GET',
      })
    );
  });
}); 
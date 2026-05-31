import {
  StoryGenerationRequest,
  StoryGenerationResponse,
  ApiError
} from '../types/api';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = (window as any).ENV?.REACT_APP_API_URL || 'http://localhost:8000';
  }

  async generateStory(request: StoryGenerationRequest): Promise<StoryGenerationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/story/generate-story`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: Failed to generate story`;
        
        try {
          const errorData: ApiError = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If JSON parsing fails, use the default error message
        }
        
        throw new Error(errorMessage);
      }

      const data: StoryGenerationResponse = await response.json();
      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unexpected error occurred while generating the story');
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService();
export default ApiService;
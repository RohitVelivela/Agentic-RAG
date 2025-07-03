interface Citation {
  id: string;
  source: string;
  content: string;
  page?: number;
  url?: string;
}

interface QueryResponse {
  answer: string;
  citations: Citation[];
  metadata: {
    sourcesSearched?: number;
    documentsFound?: number;
    webResults?: number;
    [key: string]: any;
  };
  processing_time_ms: number;
  confidence_score: number;
  sources_used: {
    document?: number;
    web?: number;
    google_drive?: number;
    [key: string]: number | undefined;
  };
}

interface UploadResponse {
  success: boolean;
  message: string;
  filename?: string;
  document_id?: string;
}

interface HealthResponse {
  status: string;
  version: string;
  services: {
    [key: string]: string;
  };
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || 
          errorData.message || 
          `HTTP error! status: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  async query(query: string): Promise<QueryResponse> {
    return this.request<QueryResponse>('/query', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<UploadResponse>('/upload', {
      method: 'POST',
      headers: {}, // Don't set Content-Type for FormData
      body: formData,
    });
  }

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async listDocuments(): Promise<string[]> {
    return this.request<string[]>('/documents');
  }

  async deleteDocument(documentId: string): Promise<{ success: boolean; message: string }> {
    return this.request('/documents/' + documentId, {
      method: 'DELETE',
    });
  }

  async searchDocuments(query: string): Promise<any[]> {
    return this.request('/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }
}

// Create a default instance
const apiClient = new ApiClient();

// Export convenience functions
export const sendQuery = (query: string) => apiClient.query(query);
export const uploadDocument = (file: File) => apiClient.uploadDocument(file);
export const getHealth = () => apiClient.getHealth();
export const listDocuments = () => apiClient.listDocuments();
export const deleteDocument = (documentId: string) => apiClient.deleteDocument(documentId);
export const searchDocuments = (query: string) => apiClient.searchDocuments(query);

// Export the client class for advanced usage
export { ApiClient };
export default apiClient; 
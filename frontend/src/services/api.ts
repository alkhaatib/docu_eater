import axios from 'axios';
import { CrawlRequest, CrawlResponse, CrawlTask, DocMap } from '../types';

// Configure axios
const API_BASE_URL = 'http://localhost:8000';
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service for communicating with the backend
export const ApiService = {
  // Start a new crawl task
  startCrawl: async (request: CrawlRequest): Promise<CrawlResponse> => {
    try {
      const response = await api.post<CrawlResponse>('/api/tasks', {
        url: request.url,
        max_depth: request.max_depth || 3,
        max_pages: request.max_pages || 100,
        respect_robots_txt: request.respect_robots_txt ?? true,
        user_agent: request.user_agent || "Docu-Eater/1.0",
        detect_nav_menu: true,
        crawl_type: request.crawl_type || "breadth"
      });
      console.log('Crawl start response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error starting crawl:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Failed to start crawl. Network or server error occurred.');
    }
  },

  // Get status of a crawl task
  getCrawlStatus: async (taskId: string): Promise<CrawlTask> => {
    try {
      const response = await api.get<CrawlTask>(`/api/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching task status for ${taskId}:`, error);
      throw error;
    }
  },

  // Get documentation map for a completed task
  getDocMap: async (taskId: string): Promise<DocMap> => {
    try {
      const response = await api.get<DocMap>(`/api/map/${taskId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching doc map for ${taskId}:`, error);
      throw error;
    }
  },

  // Get all tasks
  getAllTasks: async (): Promise<CrawlTask[]> => {
    try {
      const response = await api.get<CrawlTask[]>('/api/tasks');
      return response.data;
    } catch (error) {
      console.error('Error fetching all tasks:', error);
      // Return empty array instead of throwing to handle gracefully
      return [];
    }
  },

  // Test API connection
  testConnection: async (): Promise<boolean> => {
    try {
      await api.get('/api/test');
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }
}; 
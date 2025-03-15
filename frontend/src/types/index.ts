/**
 * Type definitions for DocuEater frontend
 */

// Crawl request parameters
export interface CrawlRequest {
  url: string;
  max_depth?: number;
  max_pages?: number;
  respect_robots_txt?: boolean;
  user_agent?: string;
  crawl_type?: string;
}

// Crawl response from API
export interface CrawlResponse {
  task_id: string;
  status: string;
  url: string;
  stats?: any;
  error?: string;
  duration?: number;
  start_time?: string;
  end_time?: string;
}

// Crawl task status
export interface CrawlTask {
  task_id: string;
  status: string;
  url: string;
  start_time?: string;
  end_time?: string;
  duration?: number;
  stats?: {
    pages_indexed?: number;
    max_pages?: number;
    links_followed?: number;
    errors?: number;
  };
  error?: string;
}

// Document map node interface
export interface DocMapNode {
  id: string;
  name: string;
  url?: string;
  children: DocMapNode[];
}

// Document map type (root node)
export type DocMap = DocMapNode; 
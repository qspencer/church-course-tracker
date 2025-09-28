/**
 * Course Content Models
 * 
 * This module defines TypeScript interfaces for course content management,
 * including modules, content items, and access tracking.
 */

export enum CourseContentType {
  DOCUMENT = 'document',
  VIDEO = 'video',
  AUDIO = 'audio',
  IMAGE = 'image',
  EXTERNAL_LINK = 'external_link',
  EMBEDDED = 'embedded'
}

export enum StorageType {
  DATABASE = 'database',
  S3 = 's3',
  EXTERNAL = 'external'
}

export interface CourseModule {
  id: number;
  course_id: number;
  title: string;
  description?: string;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
  content_items?: CourseContent[];
}

export interface CourseModuleCreate {
  course_id: number;
  title: string;
  description?: string;
  order_index?: number;
  is_active?: boolean;
}

export interface CourseModuleUpdate {
  title?: string;
  description?: string;
  order_index?: number;
  is_active?: boolean;
}

export interface CourseContent {
  id: number;
  course_id: number;
  module_id?: number;
  title: string;
  description?: string;
  content_type: CourseContentType;
  storage_type: StorageType;
  file_name?: string;
  file_size?: number;
  file_path?: string;
  mime_type?: string;
  external_url?: string;
  embedded_content?: string;
  duration?: number;
  download_count: number;
  view_count: number;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
}

export interface CourseContentCreate {
  course_id: number;
  module_id?: number;
  title: string;
  description?: string;
  content_type: CourseContentType;
  storage_type: StorageType;
  order_index?: number;
  is_active?: boolean;
  file_name?: string;
  file_size?: number;
  mime_type?: string;
  external_url?: string;
  embedded_content?: string;
  duration?: number;
}

export interface CourseContentUpdate {
  title?: string;
  description?: string;
  module_id?: number;
  content_type?: CourseContentType;
  storage_type?: StorageType;
  order_index?: number;
  is_active?: boolean;
  external_url?: string;
  embedded_content?: string;
  duration?: number;
}

export interface ContentAccessLog {
  id: number;
  content_id: number;
  user_id: number;
  access_type: 'view' | 'download' | 'complete';
  access_timestamp: string;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
  progress_percentage?: number;
  time_spent?: number;
}

export interface ContentAccessLogCreate {
  content_id: number;
  user_id: number;
  access_type: 'view' | 'download' | 'complete';
  progress_percentage?: number;
  time_spent?: number;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
}

export interface ContentAuditLogCreate {
  content_id: number;
  user_id: number;
  action: 'create' | 'update' | 'delete' | 'view';
  old_values?: any;
  new_values?: any;
  change_summary?: string;
}

export interface ContentAuditLog {
  id: number;
  content_id: number;
  user_id: number;
  action: 'create' | 'update' | 'delete' | 'view';
  change_timestamp: string;
  old_values?: any;
  new_values?: any;
  change_summary?: string;
  ip_address?: string;
  user_agent?: string;
}

export interface ContentUploadResponse {
  file_name: string;
  file_size: number;
  file_path: string;
  mime_type: string;
  message: string;
}

export interface ContentDownloadRequest {
  content_id: number;
  access_type?: 'view' | 'download' | 'complete';
}

export interface ContentProgressUpdate {
  content_id: number;
  progress_percentage: number;
  time_spent?: number;
}

export interface ContentProgress {
  content_id: number;
  content_title: string;
  last_accessed?: string;
  access_type?: 'view' | 'download' | 'complete';
  progress_percentage: number;
  time_spent: number;
}

export interface CourseContentSummary {
  course_id: number;
  total_content_items: number;
  total_modules: number;
  total_file_size: number;
  content_by_type: { [key: string]: number };
  recent_uploads: CourseContent[];
}

// Helper functions for content type display
export function getContentTypeDisplayName(contentType: CourseContentType): string {
  const displayNames: { [key in CourseContentType]: string } = {
    [CourseContentType.DOCUMENT]: 'Document',
    [CourseContentType.VIDEO]: 'Video',
    [CourseContentType.AUDIO]: 'Audio',
    [CourseContentType.IMAGE]: 'Image',
    [CourseContentType.EXTERNAL_LINK]: 'External Link',
    [CourseContentType.EMBEDDED]: 'Embedded Content'
  };
  return displayNames[contentType] || 'Unknown';
}

export function getContentTypeIcon(contentType: CourseContentType): string {
  const icons: { [key in CourseContentType]: string } = {
    [CourseContentType.DOCUMENT]: 'description',
    [CourseContentType.VIDEO]: 'play_circle',
    [CourseContentType.AUDIO]: 'audiotrack',
    [CourseContentType.IMAGE]: 'image',
    [CourseContentType.EXTERNAL_LINK]: 'link',
    [CourseContentType.EMBEDDED]: 'code'
  };
  return icons[contentType] || 'insert_drive_file';
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  } else {
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
}

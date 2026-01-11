/**
 * Program Content Models
 * 
 * This module defines TypeScript interfaces for program content management,
 * including modules (categories) and content items (lessons).
 */

// Reuse content types from course content model
export enum ContentType {
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

export interface ProgramModule {
  id: number;
  program_id: number;
  title: string;
  description?: string;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
  content_items?: ProgramContent[];
}

export interface ProgramModuleCreate {
  program_id: number;
  title: string;
  description?: string;
  order_index?: number;
  is_active?: boolean;
}

export interface ProgramModuleUpdate {
  title?: string;
  description?: string;
  order_index?: number;
  is_active?: boolean;
}

export interface ProgramContent {
  id: number;
  program_id: number;
  module_id?: number;
  shared_content_id?: number;
  title?: string;
  description?: string;
  content_type?: ContentType;
  storage_type?: StorageType;
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

export interface ProgramContentCreate {
  program_id: number;
  module_id?: number;
  shared_content_id?: number;
  title?: string;
  description?: string;
  content_type?: ContentType;
  storage_type?: StorageType;
  order_index?: number;
  is_active?: boolean;
  file_name?: string;
  file_size?: number;
  mime_type?: string;
  external_url?: string;
  embedded_content?: string;
  duration?: number;
}

export interface ProgramContentUpdate {
  title?: string;
  description?: string;
  module_id?: number;
  shared_content_id?: number;
  content_type?: ContentType;
  storage_type?: StorageType;
  order_index?: number;
  is_active?: boolean;
  external_url?: string;
  embedded_content?: string;
  duration?: number;
}

// Helper functions for content type display
export function getContentTypeDisplayName(contentType?: ContentType): string {
  if (!contentType) return 'Unknown';
  
  const displayNames: { [key in ContentType]: string } = {
    [ContentType.DOCUMENT]: 'Document',
    [ContentType.VIDEO]: 'Video',
    [ContentType.AUDIO]: 'Audio',
    [ContentType.IMAGE]: 'Image',
    [ContentType.EXTERNAL_LINK]: 'External Link',
    [ContentType.EMBEDDED]: 'Embedded Content'
  };
  return displayNames[contentType] || 'Unknown';
}

export function getContentTypeIcon(contentType?: ContentType): string {
  if (!contentType) return 'insert_drive_file';
  
  const icons: { [key in ContentType]: string } = {
    [ContentType.DOCUMENT]: 'description',
    [ContentType.VIDEO]: 'play_circle',
    [ContentType.AUDIO]: 'audiotrack',
    [ContentType.IMAGE]: 'image',
    [ContentType.EXTERNAL_LINK]: 'link',
    [ContentType.EMBEDDED]: 'code'
  };
  return icons[contentType] || 'insert_drive_file';
}

export function formatFileSize(bytes?: number): string {
  if (!bytes || bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDuration(seconds?: number): string {
  if (!seconds) return '0:00';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  } else {
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
}



export interface Course {
  id: number;
  title: string;
  description: string;
  duration_weeks: number;
  prerequisites?: number[];
  instructors?: (number | string)[]; // User IDs (numbers) and/or "TBD" string
  locations?: string[];
  delivery_modes?: string[];
  planning_center_event_id?: string;
  planning_center_event_name?: string;
  event_start_date?: string;
  event_end_date?: string;
  max_capacity?: number;
  current_registrations?: number;
  is_active: boolean;
  content_unlock_mode?: string;
  max_file_size_mb?: number;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
  created_by_user_name?: string;
  updated_by_user_name?: string;
  content_items?: Content[];
  enrollments_count?: number;
  completion_rate?: number;
}

export interface CourseCreate {
  planning_center_event_id?: string;
  planning_center_event_name?: string;
  event_start_date?: string | Date;
  event_end_date?: string | Date;
  max_capacity?: number;
  title: string;
  description: string;
  duration_weeks: number;
  prerequisites?: number[];
  instructors?: (number | string)[]; // User IDs (numbers) and/or "TBD" string
  locations?: string[];
  delivery_modes?: string[];
}

export interface CourseUpdate {
  title?: string;
  description?: string;
  duration_weeks?: number;
  is_active?: boolean;
  prerequisites?: number[];
  instructors?: (number | string)[]; // User IDs (numbers) and/or "TBD" string
  locations?: string[];
  delivery_modes?: string[];
}

export interface CourseQueryParams {
  skip?: number;
  limit?: number;
  search?: string;
  is_active?: boolean;
  instructor_id?: number;
  sort?: string;
  order?: string;
  [key: string]: string | number | boolean | undefined;
}

export interface Content {
  id: number;
  course_id: number;
  title: string;
  description: string;
  content_type_id: number;
  content_url?: string;
  sort_order: number;
  is_required: boolean;
  created_at: string;
  updated_at: string;
  content_type?: ContentType;
}

export interface ContentType {
  id: number;
  name: string;
  description: string;
}

export interface ContentCreate {
  course_id: number;
  title: string;
  description: string;
  content_type_id: number;
  content_url?: string;
  sort_order: number;
  is_required: boolean;
}

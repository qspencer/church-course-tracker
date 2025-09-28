export interface Course {
  id: number;
  title: string;
  description: string;
  duration_weeks: number;
  prerequisites?: any;
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
  content_items?: Content[];
  enrollments_count?: number;
  completion_rate?: number;
}

export interface CourseCreate {
  title: string;
  description: string;
  duration_weeks: number;
}

export interface CourseUpdate {
  title?: string;
  description?: string;
  duration_weeks?: number;
  is_active?: boolean;
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

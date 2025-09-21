export interface Course {
  id: number;
  title: string;
  description: string;
  duration_weeks: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
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

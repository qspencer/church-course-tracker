export interface DashboardStats {
  total_courses: number;
  active_courses: number;
  total_enrollments: number;
  completed_enrollments: number;
  total_members: number;
  completion_rate: number;
}

export interface CourseStats {
  course_id: number;
  course_title: string;
  total_enrollments: number;
  completed_enrollments: number;
  in_progress_enrollments: number;
  completion_rate: number;
  average_progress: number;
}

export interface MemberProgress {
  person_id: number;
  person_name: string;
  total_enrollments: number;
  completed_enrollments: number;
  in_progress_enrollments: number;
  overall_progress: number;
}

export interface ProgressReport {
  course_stats: CourseStats[];
  member_progress: MemberProgress[];
  completion_trends: CompletionTrend[];
}

export interface CompletionTrend {
  date: string;
  completions: number;
  enrollments: number;
}

export interface ReportFilters {
  start_date?: string;
  end_date?: string;
  course_ids?: number[];
  status?: string;
}

export interface CompletionTrendsResponse {
  trends: CompletionTrend[];
  period: {
    start_date: string;
    end_date: string;
  };
  course_ids: number[];
}

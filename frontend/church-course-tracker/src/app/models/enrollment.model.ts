export interface Enrollment {
  id: number;
  person_id: number;
  people_id?: number;
  course_id: number;
  enrolled_at: string;
  enrollment_date?: string;
  completion_date?: string | null;
  notes?: string | null;
  dependency_override?: boolean;
  dependency_override_by?: number | null;
  planning_center_registration_id?: string | null;
  planning_center_synced?: boolean;
  registration_status?: string | null;
  registration_notes?: string | null;
  status: EnrollmentStatus;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  person?: Person;
  people?: Person;
  course?: Course;
  progress_items?: Progress[];
}

export interface EnrollmentCreate {
  person_id: number;
  course_id: number;
}

export interface EnrollmentUpdate {
  status?: EnrollmentStatus;
  completed_at?: string;
}

export enum EnrollmentStatus {
  ENROLLED = 'enrolled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  DROPPED = 'dropped'
}

export interface Person {
  id: number;
  planning_center_id?: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  address1?: string;
  address2?: string;
  city?: string;
  state?: string;
  zip?: string;
  household_id?: string;
  household_name?: string;
  status?: string;
  join_date?: string;
  is_active?: boolean;
  last_synced_at?: string;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
  full_name?: string;
}

export interface Progress {
  id?: number | null;
  enrollment_id: number;
  content_id: number;
  status: ProgressStatus;
  completed_at?: string | null;
  time_spent_minutes?: number | null;
  score?: number | null;
  notes?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  content?: Content;
}

export enum ProgressStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed'
}

import { Course } from './course.model';
import { Content } from './course.model';

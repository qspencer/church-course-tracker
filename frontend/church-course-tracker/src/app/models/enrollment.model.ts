export interface Enrollment {
  id: number;
  person_id: number;
  course_id: number;
  enrolled_at: string;
  completed_at?: string;
  status: EnrollmentStatus;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  person?: Person;
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
  created_at: string;
  updated_at: string;
  full_name?: string;
}

export interface Progress {
  id: number;
  enrollment_id: number;
  content_id: number;
  completed_at?: string;
  status: ProgressStatus;
  created_at: string;
  updated_at: string;
  content?: Content;
}

export enum ProgressStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed'
}

import { Course } from './course.model';
import { Content } from './course.model';

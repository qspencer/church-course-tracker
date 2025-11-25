export interface Program {
  id: number;
  title: string;
  description?: string;
  role_definitions?: RoleDefinition[];
  relationship_config?: RelationshipConfig;
  locations?: string[];
  delivery_modes?: string[];
  prerequisites?: number[];
  planning_center_event_template_id?: string;
  planning_center_event_id?: string;
  planning_center_event_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
  created_by_user_name?: string;
  updated_by_user_name?: string;
}

export interface RoleDefinition {
  name: string;
  min_participants: number;
  max_participants: number;
  is_primary: boolean;
}

export interface RelationshipConfig {
  allow_multiple_secondary?: boolean;
  max_secondary_per_primary?: number;
  require_pairing?: boolean;
  progress_calculation?: 'content_based' | 'session_based' | 'custom';
}

export interface ProgramCreate {
  title: string;
  description?: string;
  role_definitions?: RoleDefinition[];
  relationship_config?: RelationshipConfig;
  locations?: string[];
  delivery_modes?: string[];
  prerequisites?: number[];
  planning_center_event_template_id?: string;
  planning_center_event_id?: string;
  planning_center_event_name?: string;
  is_active?: boolean;
}

export interface ProgramUpdate {
  title?: string;
  description?: string;
  role_definitions?: RoleDefinition[];
  relationship_config?: RelationshipConfig;
  locations?: string[];
  delivery_modes?: string[];
  prerequisites?: number[];
  planning_center_event_template_id?: string;
  planning_center_event_id?: string;
  planning_center_event_name?: string;
  is_active?: boolean;
}

export interface ProgramAdmin {
  id: number;
  program_id: number;
  user_id: number;
  can_manage_participants: boolean;
  can_manage_pairings: boolean;
  can_manage_content: boolean;
  created_at: string;
  created_by?: number;
}

export interface ProgramAdminCreate {
  program_id: number;
  user_id: number;
  can_manage_participants?: boolean;
  can_manage_pairings?: boolean;
  can_manage_content?: boolean;
}

export interface ProgramAdminUpdate {
  can_manage_participants?: boolean;
  can_manage_pairings?: boolean;
  can_manage_content?: boolean;
}

export interface ProgramParticipant {
  id: number;
  program_id: number;
  people_id: number;
  role_name: string;
  start_date: string;
  end_date?: string;
  status: 'active' | 'paused' | 'completed' | 'ended';
  notes?: string;
  progress_percentage: number;
  last_activity_date?: string;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
}

export interface ProgramParticipantCreate {
  program_id: number;
  people_id: number;
  role_name: string;
  start_date?: string;
  end_date?: string;
  status?: 'active' | 'paused' | 'completed' | 'ended';
  notes?: string;
  progress_percentage?: number;
  last_activity_date?: string;
}

export interface ProgramParticipantUpdate {
  role_name?: string;
  start_date?: string;
  end_date?: string;
  status?: 'active' | 'paused' | 'completed' | 'ended';
  notes?: string;
  progress_percentage?: number;
  last_activity_date?: string;
}

export interface ProgramPairing {
  id: number;
  program_id: number;
  primary_participant_id: number;
  secondary_participant_id: number;
  start_date: string;
  end_date?: string;
  status: 'active' | 'paused' | 'completed' | 'ended';
  notes?: string;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
}

export interface ProgramPairingCreate {
  program_id: number;
  primary_participant_id: number;
  secondary_participant_id: number;
  start_date?: string;
  end_date?: string;
  status?: 'active' | 'paused' | 'completed' | 'ended';
  notes?: string;
}

export interface ProgramPairingUpdate {
  start_date?: string;
  end_date?: string;
  status?: 'active' | 'paused' | 'completed' | 'ended';
  notes?: string;
}

export interface ProgramSession {
  id: number;
  program_id: number;
  pairing_id?: number;
  session_date: string;
  duration_minutes?: number;
  location?: string;
  session_type?: string;
  participant_ids?: number[];
  topics_covered?: string;
  notes?: string;
  content_completed?: number[];
  milestones_achieved?: string[];
  created_at: string;
  created_by?: number;
}

export interface ProgramSessionCreate {
  program_id: number;
  pairing_id?: number;
  session_date: string;
  duration_minutes?: number;
  location?: string;
  session_type?: string;
  participant_ids?: number[];
  topics_covered?: string;
  notes?: string;
  content_completed?: number[];
  milestones_achieved?: string[];
}

export interface ProgramSessionUpdate {
  session_date?: string;
  duration_minutes?: number;
  location?: string;
  session_type?: string;
  participant_ids?: number[];
  topics_covered?: string;
  notes?: string;
  content_completed?: number[];
  milestones_achieved?: string[];
}

export interface ProgramProgress {
  id: number;
  program_id: number;
  participant_id: number;
  progress_type: 'content_completion' | 'session_completion' | 'milestone';
  content_id?: number;
  completion_date?: string;
  completion_percentage?: number;
  session_id?: number;
  milestone_name?: string;
  milestone_description?: string;
  notes?: string;
  created_at: string;
  created_by?: number;
}

export interface ProgramProgressCreate {
  program_id: number;
  participant_id: number;
  progress_type: 'content_completion' | 'session_completion' | 'milestone';
  content_id?: number;
  completion_date?: string;
  completion_percentage?: number;
  session_id?: number;
  milestone_name?: string;
  milestone_description?: string;
  notes?: string;
}

export interface ProgramProgressUpdate {
  progress_type?: 'content_completion' | 'session_completion' | 'milestone';
  content_id?: number;
  completion_date?: string;
  completion_percentage?: number;
  session_id?: number;
  milestone_name?: string;
  milestone_description?: string;
  notes?: string;
}


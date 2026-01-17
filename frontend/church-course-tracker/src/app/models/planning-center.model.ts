/**
 * Planning Center integration models
 * Used for import dialogs and preview data
 */

export interface PlanningCenterEvent {
  id: string;
  type: 'event';
  attributes: {
    name: string;
    description?: string;
    starts_at?: string;
    ends_at?: string;
    location?: string;
  };
}

export interface PlanningCenterList {
  id: string;
  type: 'list';
  attributes: {
    name: string;
    description?: string;
  };
}

export interface PlanningCenterPreview {
  type: 'event' | 'list';
  id: string;
  name: string;
  description?: string;
  participantCount?: number;
  eventDates?: {
    start: string;
    end: string;
  };
  location?: string;
  attributes?: Record<string, unknown>;
}

export interface PlanningCenterImportData {
  sourceType: 'event' | 'list';
  sourceId: string;
  previewData: {
    title: string;
    description?: string;
    planning_center_event_id?: string;
    planning_center_event_name?: string;
    planning_center_list_id?: string;
    planning_center_list_name?: string;
    event_start_date?: Date | string | null;
    event_end_date?: Date | string | null;
    max_capacity?: number | null;
    locations?: string[];
    delivery_modes?: string[];
    duration_weeks?: number | null;
  };
}

export interface PlanningCenterRegistration {
  id: string;
  type: 'registration';
  attributes: {
    status: string;
    created_at: string;
    updated_at?: string;
    notes?: string;
  };
  relationships?: {
    person?: {
      data: {
        id: string;
        type: 'person';
      };
    };
    event?: {
      data: {
        id: string;
        type: 'event';
      };
    };
  };
}

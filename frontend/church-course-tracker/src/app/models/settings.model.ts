export interface SystemSetting {
  id: number;
  key: string;
  value: string | null;
  category: string;
  data_type: 'string' | 'integer' | 'boolean' | 'json';
  description: string | null;
  is_sensitive: boolean;
  created_at: string;
  updated_at: string | null;
  updated_by: number | null;
}

export interface SystemSettingsByCategory {
  [category: string]: SystemSetting[];
}

export interface SystemSettingUpdate {
  value?: string | null;
  description?: string | null;
}

export interface SystemSettingsBatchUpdate {
  settings: { [key: string]: string };
}

export interface PlanningCenterConfig {
  api_url: string;
  app_id?: string | null;
  secret?: string | null;
  access_token?: string | null;
  max_events: number;
  cache_ttl_minutes: number;
  use_mock: boolean;
}

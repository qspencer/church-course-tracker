export interface AuditLogBase {
  table_name: string;
  record_id: number;
  action: 'insert' | 'update' | 'delete';
  old_values?: { [key: string]: any };
  new_values?: { [key: string]: any };
  changed_by?: number;
  ip_address?: string;
  user_agent?: string;
}

export interface AuditLogCreate extends AuditLogBase {}

export interface AuditLog extends AuditLogBase {
  id: number;
  changed_at: string;
}

export interface AuditLogFilters {
  table_name?: string;
  action?: 'insert' | 'update' | 'delete';
  changed_by?: number;
  user_id?: number;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface AuditSummary {
  total_logs: number;
  tables_affected: number;
  actions_performed: number;
  action_breakdown: { [key: string]: number };
  table_breakdown: { [key: string]: number };
  user_breakdown?: { [key: string]: number };
  recent_activity?: Array<{
    date: string;
    count: number;
  }>;
}

export interface AuditExportOptions {
  format: 'csv' | 'json';
  start_date?: string;
  end_date?: string;
  table_name?: string;
}

// Utility functions for audit logs
export function getActionDisplayName(action: string): string {
  switch (action) {
    case 'insert': return 'Created';
    case 'update': return 'Updated';
    case 'delete': return 'Deleted';
    default: return action;
  }
}

export function getActionIcon(action: string): string {
  switch (action) {
    case 'insert': return 'add_circle';
    case 'update': return 'edit';
    case 'delete': return 'delete';
    default: return 'help';
  }
}

export function getActionColor(action: string): string {
  switch (action) {
    case 'insert': return 'primary';
    case 'update': return 'accent';
    case 'delete': return 'warn';
    default: return '';
  }
}

export function formatAuditTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

export function getTableDisplayName(tableName: string): string {
  // Convert snake_case to Title Case
  return tableName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function formatAuditValues(values: { [key: string]: any } | undefined): string {
  if (!values) return '';
  
  const formatted = Object.entries(values)
    .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
    .join(', ');
  
  return formatted.length > 100 ? formatted.substring(0, 100) + '...' : formatted;
}

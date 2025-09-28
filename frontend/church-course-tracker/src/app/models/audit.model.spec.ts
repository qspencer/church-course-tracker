import { AuditLog, AuditLogCreate, AuditLogFilters, AuditSummary } from './audit.model';

describe('Audit Models', () => {
  describe('AuditLog', () => {
    it('should create AuditLog with required fields', () => {
      const auditLog: AuditLog = {
        id: 1,
        table_name: 'courses',
        record_id: 123,
        action: 'insert',
        old_values: undefined,
        new_values: { name: 'New Course', description: 'Course description' },
        changed_by: 1,
        changed_at: '2024-01-01T00:00:00Z',
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...'
      };

      expect(auditLog.id).toBe(1);
      expect(auditLog.table_name).toBe('courses');
      expect(auditLog.record_id).toBe(123);
      expect(auditLog.action).toBe('insert');
      expect(auditLog.old_values).toBeUndefined();
      expect(auditLog.new_values).toEqual({ name: 'New Course', description: 'Course description' });
      expect(auditLog.changed_by).toBe(1);
      expect(auditLog.changed_at).toBe('2024-01-01T00:00:00Z');
      expect(auditLog.ip_address).toBe('192.168.1.1');
      expect(auditLog.user_agent).toBe('Mozilla/5.0...');
    });

    it('should handle update action with old and new values', () => {
      const auditLog: AuditLog = {
        id: 2,
        table_name: 'users',
        record_id: 456,
        action: 'update',
        old_values: { email: 'old@example.com', full_name: 'Old Name' },
        new_values: { email: 'new@example.com', full_name: 'New Name' },
        changed_by: 2,
        changed_at: '2024-01-02T00:00:00Z',
        ip_address: '10.0.0.1',
        user_agent: 'Chrome/91.0...'
      };

      expect(auditLog.action).toBe('update');
      expect(auditLog.old_values).toEqual({ email: 'old@example.com', full_name: 'Old Name' });
      expect(auditLog.new_values).toEqual({ email: 'new@example.com', full_name: 'New Name' });
    });

    it('should handle delete action with old values only', () => {
      const auditLog: AuditLog = {
        id: 3,
        table_name: 'courses',
        record_id: 789,
        action: 'delete',
        old_values: { name: 'Deleted Course', description: 'This course was deleted' },
        new_values: undefined,
        changed_by: 1,
        changed_at: '2024-01-03T00:00:00Z',
        ip_address: '172.16.0.1',
        user_agent: 'Firefox/89.0...'
      };

      expect(auditLog.action).toBe('delete');
      expect(auditLog.old_values).toEqual({ name: 'Deleted Course', description: 'This course was deleted' });
      expect(auditLog.new_values).toBeUndefined();
    });
  });

  describe('AuditLogCreate', () => {
    it('should create AuditLogCreate with required fields', () => {
      const auditLogCreate: AuditLogCreate = {
        table_name: 'courses',
        record_id: 123,
        action: 'insert',
        old_values: undefined,
        new_values: { name: 'New Course' },
        changed_by: 1,
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...'
      };

      expect(auditLogCreate.table_name).toBe('courses');
      expect(auditLogCreate.record_id).toBe(123);
      expect(auditLogCreate.action).toBe('insert');
      expect(auditLogCreate.old_values).toBeUndefined();
      expect(auditLogCreate.new_values).toEqual({ name: 'New Course' });
      expect(auditLogCreate.changed_by).toBe(1);
      expect(auditLogCreate.ip_address).toBe('192.168.1.1');
      expect(auditLogCreate.user_agent).toBe('Mozilla/5.0...');
    });

    it('should handle optional fields', () => {
      const auditLogCreate: AuditLogCreate = {
        table_name: 'users',
        record_id: 456,
        action: 'update',
        old_values: { email: 'old@example.com' },
        new_values: { email: 'new@example.com' },
        changed_by: 2
      };

      expect(auditLogCreate.ip_address).toBeUndefined();
      expect(auditLogCreate.user_agent).toBeUndefined();
    });
  });

  describe('AuditLogFilters', () => {
    it('should create AuditLogFilters with all fields', () => {
      const filters: AuditLogFilters = {
        table_name: 'courses',
        action: 'insert',
        user_id: 1,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        limit: 50,
        offset: 0,
        sort_by: 'changed_at',
        sort_order: 'desc'
      };

      expect(filters.table_name).toBe('courses');
      expect(filters.action).toBe('insert');
      expect(filters.user_id).toBe(1);
      expect(filters.start_date).toBe('2024-01-01');
      expect(filters.end_date).toBe('2024-12-31');
      expect(filters.limit).toBe(50);
      expect(filters.offset).toBe(0);
      expect(filters.sort_by).toBe('changed_at');
      expect(filters.sort_order).toBe('desc');
    });

    it('should handle partial filters', () => {
      const filters: AuditLogFilters = {
        table_name: 'users',
        action: 'update',
        limit: 25
      };

      expect(filters.table_name).toBe('users');
      expect(filters.action).toBe('update');
      expect(filters.limit).toBe(25);
      expect(filters.user_id).toBeUndefined();
      expect(filters.start_date).toBeUndefined();
      expect(filters.end_date).toBeUndefined();
      expect(filters.offset).toBeUndefined();
      expect(filters.sort_by).toBeUndefined();
      expect(filters.sort_order).toBeUndefined();
    });

    it('should handle empty filters', () => {
      const filters: AuditLogFilters = {};

      expect(filters.table_name).toBeUndefined();
      expect(filters.action).toBeUndefined();
      expect(filters.user_id).toBeUndefined();
      expect(filters.start_date).toBeUndefined();
      expect(filters.end_date).toBeUndefined();
      expect(filters.limit).toBeUndefined();
      expect(filters.offset).toBeUndefined();
      expect(filters.sort_by).toBeUndefined();
      expect(filters.sort_order).toBeUndefined();
    });
  });

  describe('AuditSummary', () => {
    it('should create AuditSummary with all fields', () => {
      const summary: AuditSummary = {
        total_logs: 100,
        tables_affected: 5,
        actions_performed: 3,
        table_breakdown: {
          'courses': 50,
          'users': 30,
          'enrollments': 20
        },
        action_breakdown: {
          'insert': 40,
          'update': 35,
          'delete': 25
        }
      };

      expect(summary.total_logs).toBe(100);
      expect(summary.tables_affected).toBe(5);
      expect(summary.actions_performed).toBe(3);
      expect(summary.table_breakdown).toEqual({
        'courses': 50,
        'users': 30,
        'enrollments': 20
      });
      expect(summary.action_breakdown).toEqual({
        'insert': 40,
        'update': 35,
        'delete': 25
      });
    });

    it('should handle empty breakdowns', () => {
      const summary: AuditSummary = {
        total_logs: 0,
        tables_affected: 0,
        actions_performed: 0,
        table_breakdown: {},
        action_breakdown: {}
      };

      expect(summary.total_logs).toBe(0);
      expect(summary.tables_affected).toBe(0);
      expect(summary.actions_performed).toBe(0);
      expect(summary.table_breakdown).toEqual({});
      expect(summary.action_breakdown).toEqual({});
    });

    it('should handle single table and action', () => {
      const summary: AuditSummary = {
        total_logs: 10,
        tables_affected: 1,
        actions_performed: 1,
        table_breakdown: {
          'courses': 10
        },
        action_breakdown: {
          'insert': 10
        }
      };

      expect(summary.total_logs).toBe(10);
      expect(summary.tables_affected).toBe(1);
      expect(summary.actions_performed).toBe(1);
      expect(summary.table_breakdown).toEqual({ 'courses': 10 });
      expect(summary.action_breakdown).toEqual({ 'insert': 10 });
    });
  });

  describe('Model Validation', () => {
    it('should handle null values in AuditLog', () => {
      const auditLog: AuditLog = {
        id: 1,
        table_name: 'test_table',
        record_id: 1,
        action: 'insert',
        old_values: undefined,
        new_values: undefined,
        changed_by: undefined,
        changed_at: '2024-01-01T00:00:00Z',
        ip_address: undefined,
        user_agent: undefined
      };

      expect(auditLog.old_values).toBeUndefined();
      expect(auditLog.new_values).toBeUndefined();
      expect(auditLog.changed_by).toBeUndefined();
      expect(auditLog.ip_address).toBeUndefined();
      expect(auditLog.user_agent).toBeUndefined();
    });

    it('should handle undefined values in AuditLogCreate', () => {
      const auditLogCreate: AuditLogCreate = {
        table_name: 'test_table',
        record_id: 1,
        action: 'insert',
        old_values: undefined,
        new_values: undefined,
        changed_by: undefined,
        ip_address: undefined,
        user_agent: undefined
      };

      expect(auditLogCreate.old_values).toBeUndefined();
      expect(auditLogCreate.new_values).toBeUndefined();
      expect(auditLogCreate.changed_by).toBeUndefined();
      expect(auditLogCreate.ip_address).toBeUndefined();
      expect(auditLogCreate.user_agent).toBeUndefined();
    });

    it('should handle complex JSON values', () => {
      const complexOldValues = {
        nested: {
          array: [1, 2, 3],
          object: { key: 'value' }
        },
        simple: 'string'
      };

      const complexNewValues = {
        updated: true,
        metadata: {
          version: '2.0',
          features: ['feature1', 'feature2']
        }
      };

      const auditLog: AuditLog = {
        id: 1,
        table_name: 'complex_table',
        record_id: 1,
        action: 'update',
        old_values: complexOldValues,
        new_values: complexNewValues,
        changed_by: 1,
        changed_at: '2024-01-01T00:00:00Z',
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...'
      };

      expect(auditLog.old_values).toEqual(complexOldValues);
      expect(auditLog.new_values).toEqual(complexNewValues);
      expect(auditLog.old_values?.['nested']?.['array']).toEqual([1, 2, 3]);
      expect(auditLog.new_values?.['metadata']?.['version']).toBe('2.0');
    });
  });

  describe('Action Types', () => {
    it('should handle all valid action types', () => {
      const actions = ['insert', 'update', 'delete'];
      
      actions.forEach(action => {
        const auditLog: AuditLog = {
          id: 1,
          table_name: 'test_table',
          record_id: 1,
          action: action as 'insert' | 'update' | 'delete',
          old_values: undefined,
          new_values: undefined,
          changed_by: 1,
          changed_at: '2024-01-01T00:00:00Z',
          ip_address: '192.168.1.1',
          user_agent: 'Mozilla/5.0...'
        };

        expect(auditLog.action).toBe(action);
      });
    });
  });

  describe('Table Names', () => {
    it('should handle various table names', () => {
      const tableNames = ['courses', 'users', 'enrollments', 'course_content', 'audit_logs'];
      
      tableNames.forEach(tableName => {
        const auditLog: AuditLog = {
          id: 1,
          table_name: tableName,
          record_id: 1,
          action: 'insert',
          old_values: undefined,
          new_values: undefined,
          changed_by: 1,
          changed_at: '2024-01-01T00:00:00Z',
          ip_address: '192.168.1.1',
          user_agent: 'Mozilla/5.0...'
        };

        expect(auditLog.table_name).toBe(tableName);
      });
    });
  });

  describe('Date Handling', () => {
    it('should handle ISO date strings', () => {
      const dates = [
        '2024-01-01T00:00:00Z',
        '2024-12-31T23:59:59Z',
        '2024-06-15T12:30:45.123Z'
      ];

      dates.forEach(date => {
        const auditLog: AuditLog = {
          id: 1,
          table_name: 'test_table',
          record_id: 1,
          action: 'insert',
          old_values: undefined,
          new_values: undefined,
          changed_by: 1,
          changed_at: date,
          ip_address: '192.168.1.1',
          user_agent: 'Mozilla/5.0...'
        };

        expect(auditLog.changed_at).toBe(date);
      });
    });
  });

  describe('IP Address Handling', () => {
    it('should handle various IP address formats', () => {
      const ipAddresses = [
        '192.168.1.1',
        '10.0.0.1',
        '172.16.0.1',
        '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
        '::1'
      ];

      ipAddresses.forEach(ip => {
        const auditLog: AuditLog = {
          id: 1,
          table_name: 'test_table',
          record_id: 1,
          action: 'insert',
          old_values: undefined,
          new_values: undefined,
          changed_by: 1,
          changed_at: '2024-01-01T00:00:00Z',
          ip_address: ip,
          user_agent: 'Mozilla/5.0...'
        };

        expect(auditLog.ip_address).toBe(ip);
      });
    });
  });

  describe('User Agent Handling', () => {
    it('should handle various user agent strings', () => {
      const userAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
      ];

      userAgents.forEach(userAgent => {
        const auditLog: AuditLog = {
          id: 1,
          table_name: 'test_table',
          record_id: 1,
          action: 'insert',
          old_values: undefined,
          new_values: undefined,
          changed_by: 1,
          changed_at: '2024-01-01T00:00:00Z',
          ip_address: '192.168.1.1',
          user_agent: userAgent
        };

        expect(auditLog.user_agent).toBe(userAgent);
      });
    });
  });
});

import {
  CourseModule, CourseModuleCreate, CourseModuleUpdate,
  CourseContent, CourseContentCreate, CourseContentUpdate,
  ContentAccessLog, ContentAccessLogCreate,
  ContentAuditLog, ContentAuditLogCreate,
  ContentUploadResponse, ContentDownloadRequest, ContentProgressUpdate,
  CourseContentSummary, CourseContentType, StorageType,
  getContentTypeDisplayName, getContentTypeIcon, formatFileSize, formatDuration
} from './course-content.model';

describe('Course Content Models', () => {
  describe('CourseModule', () => {
    it('should create CourseModule with required fields', () => {
      const module: CourseModule = {
        id: 1,
        course_id: 1,
        title: 'Test Module',
        description: 'Test Description',
        order_index: 1,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        created_by: 1,
        updated_by: 1,
        content_items: []
      };

      expect(module.id).toBe(1);
      expect(module.course_id).toBe(1);
      expect(module.title).toBe('Test Module');
      expect(module.description).toBe('Test Description');
      expect(module.order_index).toBe(1);
      expect(module.is_active).toBe(true);
      expect(module.created_at).toBe('2024-01-01T00:00:00Z');
      expect(module.updated_at).toBe('2024-01-01T00:00:00Z');
      expect(module.created_by).toBe(1);
      expect(module.updated_by).toBe(1);
      expect(module.content_items).toEqual([]);
    });
  });

  describe('CourseModuleCreate', () => {
    it('should create CourseModuleCreate with required fields', () => {
      const moduleCreate: CourseModuleCreate = {
        course_id: 1,
        title: 'New Module',
        description: 'New Description',
        order_index: 1
      };

      expect(moduleCreate.course_id).toBe(1);
      expect(moduleCreate.title).toBe('New Module');
      expect(moduleCreate.description).toBe('New Description');
      expect(moduleCreate.order_index).toBe(1);
    });
  });

  describe('CourseModuleUpdate', () => {
    it('should create CourseModuleUpdate with optional fields', () => {
      const moduleUpdate: CourseModuleUpdate = {
        title: 'Updated Module',
        description: 'Updated Description',
        order_index: 2,
        is_active: false
      };

      expect(moduleUpdate.title).toBe('Updated Module');
      expect(moduleUpdate.description).toBe('Updated Description');
      expect(moduleUpdate.order_index).toBe(2);
      expect(moduleUpdate.is_active).toBe(false);
    });
  });

  describe('CourseContent', () => {
    it('should create CourseContent with required fields', () => {
      const content: CourseContent = {
        id: 1,
        course_id: 1,
        module_id: 1,
        title: 'Test Content',
        description: 'Test Description',
        content_type: CourseContentType.DOCUMENT,
        storage_type: StorageType.DATABASE,
        file_name: 'test.pdf',
        file_size: 1024,
        file_path: '/path/to/file',
        mime_type: 'application/pdf',
        external_url: undefined,
        embedded_content: undefined,
        duration: undefined,
        download_count: 0,
        view_count: 0,
        order_index: 1,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        created_by: 1,
        updated_by: 1
      };

      expect(content.id).toBe(1);
      expect(content.course_id).toBe(1);
      expect(content.module_id).toBe(1);
      expect(content.title).toBe('Test Content');
      expect(content.content_type).toBe(CourseContentType.DOCUMENT);
      expect(content.storage_type).toBe(StorageType.DATABASE);
      expect(content.file_name).toBe('test.pdf');
      expect(content.file_size).toBe(1024);
      expect(content.download_count).toBe(0);
      expect(content.view_count).toBe(0);
    });
  });

  describe('CourseContentCreate', () => {
    it('should create CourseContentCreate with required fields', () => {
      const contentCreate: CourseContentCreate = {
        course_id: 1,
        module_id: 1,
        title: 'New Content',
        description: 'New Description',
        content_type: CourseContentType.VIDEO,
        storage_type: StorageType.S3,
        order_index: 1
      };

      expect(contentCreate.course_id).toBe(1);
      expect(contentCreate.module_id).toBe(1);
      expect(contentCreate.title).toBe('New Content');
      expect(contentCreate.content_type).toBe(CourseContentType.VIDEO);
      expect(contentCreate.storage_type).toBe(StorageType.S3);
      expect(contentCreate.order_index).toBe(1);
    });
  });

  describe('CourseContentUpdate', () => {
    it('should create CourseContentUpdate with optional fields', () => {
      const contentUpdate: CourseContentUpdate = {
        title: 'Updated Content',
        description: 'Updated Description',
        content_type: CourseContentType.AUDIO,
        storage_type: StorageType.DATABASE,
        order_index: 2,
        is_active: false
      };

      expect(contentUpdate.title).toBe('Updated Content');
      expect(contentUpdate.description).toBe('Updated Description');
      expect(contentUpdate.content_type).toBe(CourseContentType.AUDIO);
      expect(contentUpdate.storage_type).toBe(StorageType.DATABASE);
      expect(contentUpdate.order_index).toBe(2);
      expect(contentUpdate.is_active).toBe(false);
    });
  });

  describe('ContentAccessLog', () => {
    it('should create ContentAccessLog with required fields', () => {
      const accessLog: ContentAccessLog = {
        id: 1,
        content_id: 1,
        user_id: 1,
        access_type: 'view',
        access_timestamp: '2024-01-01T00:00:00Z',
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...',
        session_id: 'session_123',
        progress_percentage: 50,
        time_spent: 120
      };

      expect(accessLog.id).toBe(1);
      expect(accessLog.content_id).toBe(1);
      expect(accessLog.user_id).toBe(1);
      expect(accessLog.access_type).toBe('view');
      expect(accessLog.access_timestamp).toBe('2024-01-01T00:00:00Z');
      expect(accessLog.ip_address).toBe('192.168.1.1');
      expect(accessLog.progress_percentage).toBe(50);
      expect(accessLog.time_spent).toBe(120);
    });
  });

  describe('ContentAccessLogCreate', () => {
    it('should create ContentAccessLogCreate with required fields', () => {
      const accessLogCreate: ContentAccessLogCreate = {
        content_id: 1,
        user_id: 1,
        access_type: 'download',
        progress_percentage: 100,
        time_spent: 60
      };

      expect(accessLogCreate.content_id).toBe(1);
      expect(accessLogCreate.user_id).toBe(1);
      expect(accessLogCreate.access_type).toBe('download');
      expect(accessLogCreate.progress_percentage).toBe(100);
      expect(accessLogCreate.time_spent).toBe(60);
    });
  });

  describe('ContentAuditLog', () => {
    it('should create ContentAuditLog with required fields', () => {
      const auditLog: ContentAuditLog = {
        id: 1,
        content_id: 1,
        user_id: 1,
        action: 'create',
        change_timestamp: '2024-01-01T00:00:00Z',
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...',
        change_summary: 'Content created',
        old_values: null,
        new_values: { title: 'Test Content' }
      };

      expect(auditLog.id).toBe(1);
      expect(auditLog.content_id).toBe(1);
      expect(auditLog.user_id).toBe(1);
      expect(auditLog.action).toBe('create');
      expect(auditLog.change_timestamp).toBe('2024-01-01T00:00:00Z');
      expect(auditLog.change_summary).toBe('Content created');
      expect(auditLog.old_values).toBeNull();
      expect(auditLog.new_values).toEqual({ title: 'Test Content' });
    });
  });

  describe('ContentAuditLogCreate', () => {
    it('should create ContentAuditLogCreate with required fields', () => {
      const auditLogCreate: ContentAuditLogCreate = {
        content_id: 1,
        user_id: 1,
        action: 'update',
        change_summary: 'Content updated',
        old_values: { title: 'Old Title' },
        new_values: { title: 'New Title' }
      };

      expect(auditLogCreate.content_id).toBe(1);
      expect(auditLogCreate.user_id).toBe(1);
      expect(auditLogCreate.action).toBe('update');
      expect(auditLogCreate.change_summary).toBe('Content updated');
      expect(auditLogCreate.old_values).toEqual({ title: 'Old Title' });
      expect(auditLogCreate.new_values).toEqual({ title: 'New Title' });
    });
  });

  describe('ContentUploadResponse', () => {
    it('should create ContentUploadResponse with required fields', () => {
      const uploadResponse: ContentUploadResponse = {
        file_name: 'test.pdf',
        file_size: 1024,
        file_path: '/path/to/file',
        mime_type: 'application/pdf',
        message: 'File uploaded successfully'
      };

      expect(uploadResponse.file_name).toBe('test.pdf');
      expect(uploadResponse.file_size).toBe(1024);
      expect(uploadResponse.file_path).toBe('/path/to/file');
      expect(uploadResponse.mime_type).toBe('application/pdf');
      expect(uploadResponse.message).toBe('File uploaded successfully');
    });
  });

  describe('ContentDownloadRequest', () => {
    it('should create ContentDownloadRequest with required fields', () => {
      const downloadRequest: ContentDownloadRequest = {
        content_id: 1,
        access_type: 'download'
      };

      expect(downloadRequest.content_id).toBe(1);
      expect(downloadRequest.access_type).toBe('download');
    });
  });

  describe('ContentProgressUpdate', () => {
    it('should create ContentProgressUpdate with required fields', () => {
      const progressUpdate: ContentProgressUpdate = {
        content_id: 1,
        progress_percentage: 75,
        time_spent: 180
      };

      expect(progressUpdate.content_id).toBe(1);
      expect(progressUpdate.progress_percentage).toBe(75);
      expect(progressUpdate.time_spent).toBe(180);
    });
  });

  describe('CourseContentSummary', () => {
    it('should create CourseContentSummary with required fields', () => {
      const summary: CourseContentSummary = {
        course_id: 1,
        total_content_items: 10,
        total_modules: 3,
        total_file_size: 1024000,
        content_by_type: {
          'document': 5,
          'video': 3,
          'audio': 2
        },
        recent_uploads: []
      };

      expect(summary.course_id).toBe(1);
      expect(summary.total_content_items).toBe(10);
      expect(summary.total_modules).toBe(3);
      expect(summary.total_file_size).toBe(1024000);
      expect(summary.content_by_type).toEqual({
        'document': 5,
        'video': 3,
        'audio': 2
      });
      expect(summary.recent_uploads).toEqual([]);
    });
  });

  describe('CourseContentType Enum', () => {
    it('should have correct enum values', () => {
      expect(CourseContentType.DOCUMENT).toBe('document');
      expect(CourseContentType.VIDEO).toBe('video');
      expect(CourseContentType.AUDIO).toBe('audio');
      expect(CourseContentType.IMAGE).toBe('image');
      expect(CourseContentType.EXTERNAL_LINK).toBe('external_link');
      expect(CourseContentType.EMBEDDED).toBe('embedded');
    });
  });

  describe('StorageType Enum', () => {
    it('should have correct enum values', () => {
      expect(StorageType.DATABASE).toBe('database');
      expect(StorageType.S3).toBe('s3');
      expect(StorageType.EXTERNAL).toBe('external');
    });
  });

  describe('Utility Functions', () => {
    describe('getContentTypeDisplayName', () => {
      it('should return correct display names', () => {
        expect(getContentTypeDisplayName(CourseContentType.DOCUMENT)).toBe('Document');
        expect(getContentTypeDisplayName(CourseContentType.VIDEO)).toBe('Video');
        expect(getContentTypeDisplayName(CourseContentType.AUDIO)).toBe('Audio');
        expect(getContentTypeDisplayName(CourseContentType.IMAGE)).toBe('Image');
        expect(getContentTypeDisplayName(CourseContentType.EXTERNAL_LINK)).toBe('External Link');
        expect(getContentTypeDisplayName(CourseContentType.EMBEDDED)).toBe('Embedded Content');
      });

      it('should return Unknown for invalid type', () => {
        expect(getContentTypeDisplayName('invalid' as CourseContentType)).toBe('Unknown');
      });
    });

    describe('getContentTypeIcon', () => {
      it('should return correct icons', () => {
        expect(getContentTypeIcon(CourseContentType.DOCUMENT)).toBe('description');
        expect(getContentTypeIcon(CourseContentType.VIDEO)).toBe('play_circle');
        expect(getContentTypeIcon(CourseContentType.AUDIO)).toBe('audiotrack');
        expect(getContentTypeIcon(CourseContentType.IMAGE)).toBe('image');
        expect(getContentTypeIcon(CourseContentType.EXTERNAL_LINK)).toBe('link');
        expect(getContentTypeIcon(CourseContentType.EMBEDDED)).toBe('code');
      });

      it('should return default icon for invalid type', () => {
        expect(getContentTypeIcon('invalid' as CourseContentType)).toBe('insert_drive_file');
      });
    });

    describe('formatFileSize', () => {
      it('should format file sizes correctly', () => {
        expect(formatFileSize(0)).toBe('0 Bytes');
        expect(formatFileSize(1024)).toBe('1 KB');
        expect(formatFileSize(1048576)).toBe('1 MB');
        expect(formatFileSize(1073741824)).toBe('1 GB');
        expect(formatFileSize(1536)).toBe('1.5 KB');
        expect(formatFileSize(1572864)).toBe('1.5 MB');
      });

      it('should handle large file sizes', () => {
        expect(formatFileSize(1099511627776)).toBe('1 TB');
        expect(formatFileSize(1125899906842624)).toBe('1 PB');
      });
    });

    describe('formatDuration', () => {
      it('should format durations correctly', () => {
        expect(formatDuration(0)).toBe('0:00');
        expect(formatDuration(30)).toBe('0:30');
        expect(formatDuration(60)).toBe('1:00');
        expect(formatDuration(90)).toBe('1:30');
        expect(formatDuration(3600)).toBe('1:00:00');
        expect(formatDuration(3661)).toBe('1:01:01');
        expect(formatDuration(7322)).toBe('2:02:02');
      });

      it('should handle edge cases', () => {
        expect(formatDuration(59)).toBe('0:59');
        expect(formatDuration(3599)).toBe('59:59');
        expect(formatDuration(3601)).toBe('1:00:01');
      });
    });
  });

  describe('Model Validation', () => {
    it('should handle optional fields correctly', () => {
      const content: CourseContent = {
        id: 1,
        course_id: 1,
        title: 'Test Content',
        content_type: CourseContentType.DOCUMENT,
        storage_type: StorageType.DATABASE,
        order_index: 1,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        download_count: 0,
        view_count: 0
      };

      expect(content.module_id).toBeUndefined();
      expect(content.description).toBeUndefined();
      expect(content.file_name).toBeUndefined();
      expect(content.file_size).toBeUndefined();
      expect(content.file_path).toBeUndefined();
      expect(content.mime_type).toBeUndefined();
      expect(content.external_url).toBeUndefined();
      expect(content.embedded_content).toBeUndefined();
      expect(content.duration).toBeUndefined();
      expect(content.created_by).toBeUndefined();
      expect(content.updated_by).toBeUndefined();
    });

    it('should handle null values correctly', () => {
      const content: CourseContent = {
        id: 1,
        course_id: 1,
        module_id: undefined,
        title: 'Test Content',
        description: undefined,
        content_type: CourseContentType.DOCUMENT,
        storage_type: StorageType.DATABASE,
        file_name: undefined,
        file_size: undefined,
        file_path: undefined,
        mime_type: undefined,
        external_url: undefined,
        embedded_content: undefined,
        duration: undefined,
        order_index: 1,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        created_by: undefined,
        updated_by: undefined,
        download_count: 0,
        view_count: 0
      };

      expect(content.module_id).toBeUndefined();
      expect(content.description).toBeUndefined();
      expect(content.file_name).toBeUndefined();
      expect(content.file_size).toBeUndefined();
      expect(content.file_path).toBeUndefined();
      expect(content.mime_type).toBeUndefined();
      expect(content.external_url).toBeUndefined();
      expect(content.embedded_content).toBeUndefined();
      expect(content.duration).toBeUndefined();
      expect(content.created_by).toBeUndefined();
      expect(content.updated_by).toBeUndefined();
    });
  });
});

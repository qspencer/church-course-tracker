/**
 * Advanced Course Content Management E2E Tests
 * 
 * Tests for file upload, progress tracking, audit logs, and content management
 * functionality in the course content system.
 */

import { test, expect } from '@playwright/test';

// Test users for different roles
const testUsers = {
  admin: { username: 'admin', password: 'admin123' },
  staff: { username: 'staff', password: 'staff123' },
  viewer: { username: 'viewer', password: 'viewer123' }
};

// Helper function to login as a specific user
async function loginAs(page: any, user: { username: string; password: string }) {
  await page.goto('/auth');
  await page.fill('input[name="username"]', user.username);
  await page.fill('input[name="password"]', user.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
}

// Helper function to navigate to course content management
async function navigateToCourseContent(page: any) {
  await page.click('text=Courses');
  await page.click('text=Course Content');
  await page.waitForLoadState('networkidle');
}

test.describe('Course Content File Operations', () => {
  test('Admin can upload files to course content', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    // Create a new course if needed
    await page.click('button:has-text("Create Course")');
    await page.fill('input[name="title"]', 'File Upload Test Course');
    await page.fill('textarea[name="description"]', 'Course for testing file uploads');
    await page.click('button:has-text("Save Course")');
    await expect(page.locator('text=Course created successfully')).toBeVisible();

    // Navigate to course content
    await page.click('text=View Content');
    await page.waitForLoadState('networkidle');

    // Create a module
    await page.click('button:has-text("Add Module")');
    await page.fill('input[name="title"]', 'File Upload Module');
    await page.fill('textarea[name="description"]', 'Module for file uploads');
    await page.click('button:has-text("Save Module")');
    await expect(page.locator('text=Module created successfully')).toBeVisible();

    // Create content item
    await page.click('button:has-text("Add Content")');
    await page.fill('input[name="title"]', 'Test Document');
    await page.selectOption('select[name="content_type"]', 'document');
    await page.selectOption('select[name="storage_type"]', 'database');
    await page.click('button:has-text("Save Content")');
    await expect(page.locator('text=Content created successfully')).toBeVisible();

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-document.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('test file content for upload')
    });

    await page.click('button:has-text("Upload File")');
    await expect(page.locator('text=File uploaded successfully')).toBeVisible();
    await expect(page.locator('text=test-document.pdf')).toBeVisible();
  });

  test('Admin can download uploaded files', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    // Navigate to existing content with uploaded file
    await page.click('text=View Content');
    await page.click('text=Test Document');
    
    // Click download button
    await page.click('button:has-text("Download")');
    
    // Verify download started (this will depend on browser behavior)
    await expect(page.locator('text=Download started')).toBeVisible();
  });

  test('File upload shows validation errors for invalid files', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');

    // Try to upload invalid file type
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test.exe',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('executable content')
    });

    await page.click('button:has-text("Upload File")');
    await expect(page.locator('text=Invalid file type')).toBeVisible();
  });

  test('Staff can upload files but not download audit logs', async ({ page }) => {
    await loginAs(page, testUsers.staff);
    await navigateToCourseContent(page);

    // Staff can upload files
    await page.click('text=View Content');
    await page.click('text=Test Document');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'staff-document.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('staff uploaded content')
    });

    await page.click('button:has-text("Upload File")');
    await expect(page.locator('text=File uploaded successfully')).toBeVisible();

    // Staff cannot access audit logs
    await expect(page.locator('button:has-text("View Audit Logs")')).not.toBeVisible();
  });

  test('Viewer cannot upload files', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');

    // Viewer should not see upload button
    await expect(page.locator('button:has-text("Upload File")')).not.toBeVisible();
    
    // Viewer can download files
    await expect(page.locator('button:has-text("Download")')).toBeVisible();
  });
});

test.describe('Course Content Progress Tracking', () => {
  test('User can track progress for video content', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);

    await page.click('text=My Courses');
    await page.click('text=View Course');
    await page.click('text=Video Content');

    // Start video
    await page.click('button:has-text("Play")');
    
    // Simulate progress tracking
    await page.waitForTimeout(2000); // Simulate 2 seconds of viewing
    
    // Update progress
    await page.click('button:has-text("Update Progress")');
    await page.fill('input[name="progress_percentage"]', '25');
    await page.fill('input[name="time_spent"]', '120');
    await page.click('button:has-text("Save Progress")');
    
    await expect(page.locator('text=Progress updated successfully')).toBeVisible();
    await expect(page.locator('text=25% complete')).toBeVisible();
  });

  test('User can mark content as complete', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);

    await page.click('text=My Courses');
    await page.click('text=View Course');
    await page.click('text=Video Content');

    // Mark as complete
    await page.click('button:has-text("Mark Complete")');
    await expect(page.locator('text=Content marked as complete')).toBeVisible();
    await expect(page.locator('text=100% complete')).toBeVisible();
  });

  test('Progress is persisted across sessions', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);

    await page.click('text=My Courses');
    await page.click('text=View Course');
    await page.click('text=Video Content');

    // Verify previous progress is shown
    await expect(page.locator('text=100% complete')).toBeVisible();
  });

  test('Admin can view user progress reports', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=Reports');
    await page.click('text=User Progress');
    
    // Select a user
    await page.selectOption('select[name="user"]', 'viewer');
    await page.click('button:has-text("Generate Report")');
    
    await expect(page.locator('text=Progress Report')).toBeVisible();
    await expect(page.locator('text=100% complete')).toBeVisible();
  });
});

test.describe('Course Content Audit Logs', () => {
  test('Admin can view content audit logs', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');
    await page.click('button:has-text("View Audit Logs")');
    
    await expect(page.locator('text=Audit Logs')).toBeVisible();
    await expect(page.locator('text=Content created')).toBeVisible();
    await expect(page.locator('text=File uploaded')).toBeVisible();
  });

  test('Audit logs show user actions and timestamps', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');
    await page.click('button:has-text("View Audit Logs")');
    
    // Verify audit log entries
    const auditEntries = page.locator('.audit-log-entry');
    await expect(auditEntries).toHaveCount(2); // Create and upload actions
    
    // Check first entry (most recent)
    await expect(auditEntries.first().locator('text=File uploaded')).toBeVisible();
    await expect(auditEntries.first().locator('text=admin')).toBeVisible();
    
    // Check second entry
    await expect(auditEntries.nth(1).locator('text=Content created')).toBeVisible();
  });

  test('Staff cannot view audit logs', async ({ page }) => {
    await loginAs(page, testUsers.staff);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');
    
    // Staff should not see audit logs button
    await expect(page.locator('button:has-text("View Audit Logs")')).not.toBeVisible();
  });

  test('Audit logs are updated when content is modified', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');
    
    // Edit content
    await page.click('button:has-text("Edit")');
    await page.fill('input[name="title"]', 'Updated Test Document');
    await page.click('button:has-text("Save Changes")');
    await expect(page.locator('text=Content updated successfully')).toBeVisible();
    
    // View audit logs
    await page.click('button:has-text("View Audit Logs")');
    await expect(page.locator('text=Content updated')).toBeVisible();
  });
});

test.describe('Course Content Summary and Reports', () => {
  test('Admin can view course content summary', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('button:has-text("Content Summary")');
    
    await expect(page.locator('text=Course Content Summary')).toBeVisible();
    await expect(page.locator('text=Total Modules: 1')).toBeVisible();
    await expect(page.locator('text=Total Content: 1')).toBeVisible();
    await expect(page.locator('text=Document: 1')).toBeVisible();
  });

  test('Content summary shows module breakdown', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('button:has-text("Content Summary")');
    
    // Check module details
    await expect(page.locator('text=File Upload Module')).toBeVisible();
    await expect(page.locator('text=1 content items')).toBeVisible();
  });

  test('Content summary shows content type breakdown', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('button:has-text("Content Summary")');
    
    // Check content type statistics
    await expect(page.locator('text=Content Types:')).toBeVisible();
    await expect(page.locator('text=Document: 1')).toBeVisible();
  });

  test('Staff can view content summary but not detailed reports', async ({ page }) => {
    await loginAs(page, testUsers.staff);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('button:has-text("Content Summary")');
    
    await expect(page.locator('text=Course Content Summary')).toBeVisible();
    
    // Staff should not see detailed audit information
    await expect(page.locator('text=Audit Details')).not.toBeVisible();
  });
});

test.describe('Course Content Role-Based Access', () => {
  test('Admin has full access to all content operations', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    // Admin can create courses
    await expect(page.locator('button:has-text("Create Course")')).toBeVisible();
    
    // Admin can manage content
    await page.click('text=View Content');
    await expect(page.locator('button:has-text("Add Module")')).toBeVisible();
    await expect(page.locator('button:has-text("Add Content")')).toBeVisible();
    
    // Admin can view audit logs
    await page.click('text=Test Document');
    await expect(page.locator('button:has-text("View Audit Logs")')).toBeVisible();
    
    // Admin can view reports
    await expect(page.locator('text=Reports')).toBeVisible();
  });

  test('Staff can manage content but not view audit logs', async ({ page }) => {
    await loginAs(page, testUsers.staff);
    await navigateToCourseContent(page);

    // Staff can create courses
    await expect(page.locator('button:has-text("Create Course")')).toBeVisible();
    
    // Staff can manage content
    await page.click('text=View Content');
    await expect(page.locator('button:has-text("Add Module")')).toBeVisible();
    await expect(page.locator('button:has-text("Add Content")')).toBeVisible();
    
    // Staff cannot view audit logs
    await page.click('text=Test Document');
    await expect(page.locator('button:has-text("View Audit Logs")')).not.toBeVisible();
    
    // Staff can view basic reports
    await expect(page.locator('text=Reports')).toBeVisible();
  });

  test('Viewer can access content but not manage it', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);

    // Viewer cannot create courses
    await expect(page.locator('button:has-text("Create Course")')).not.toBeVisible();
    
    // Viewer can view content
    await page.click('text=My Courses');
    await page.click('text=View Course');
    await expect(page.locator('text=Course Content')).toBeVisible();
    
    // Viewer cannot manage content
    await expect(page.locator('button:has-text("Add Module")')).not.toBeVisible();
    await expect(page.locator('button:has-text("Add Content")')).not.toBeVisible();
    
    // Viewer cannot view audit logs
    await expect(page.locator('button:has-text("View Audit Logs")')).not.toBeVisible();
    
    // Viewer cannot view reports
    await expect(page.locator('text=Reports')).not.toBeVisible();
  });
});

test.describe('Course Content Error Handling', () => {
  test('File upload shows error for invalid file types', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');

    // Try to upload executable file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'malicious.exe',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('executable content')
    });

    await page.click('button:has-text("Upload File")');
    await expect(page.locator('text=Invalid file type. Only PDF, DOC, DOCX, MP4, MP3 files are allowed.')).toBeVisible();
  });

  test('Progress tracking shows error for invalid values', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);

    await page.click('text=My Courses');
    await page.click('text=View Course');
    await page.click('text=Video Content');

    // Try to set invalid progress
    await page.fill('input[name="progress_percentage"]', '150');
    await page.click('button:has-text("Update Progress")');
    
    await expect(page.locator('text=Progress percentage must be between 0 and 100')).toBeVisible();
  });

  test('Content access shows error for non-existent content', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    
    // Try to access non-existent content directly
    await page.goto('/content/999');
    await expect(page.locator('text=Content not found')).toBeVisible();
  });

  test('Unauthorized access shows appropriate error messages', async ({ page }) => {
    // Try to access content without login
    await page.goto('/content/1');
    await expect(page.locator('text=Please log in to access this content')).toBeVisible();
    
    // Login as viewer and try to access admin functions
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);
    
    await page.click('text=View Content');
    await page.click('text=Test Document');
    
    // Try to access admin-only features
    await expect(page.locator('button:has-text("View Audit Logs")')).not.toBeVisible();
  });
});

test.describe('Course Content Performance and Usability', () => {
  test('File upload shows progress indicator', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    await page.click('text=Test Document');

    // Upload large file
    const largeContent = Buffer.alloc(1024 * 1024, 'a'); // 1MB file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'large-file.pdf',
      mimeType: 'application/pdf',
      buffer: largeContent
    });

    await page.click('button:has-text("Upload File")');
    
    // Check for progress indicator
    await expect(page.locator('text=Uploading...')).toBeVisible();
    await expect(page.locator('.progress-bar')).toBeVisible();
  });

  test('Content list loads efficiently with many items', async ({ page }) => {
    await loginAs(page, testUsers.admin);
    await navigateToCourseContent(page);

    await page.click('text=View Content');
    
    // Check that content loads quickly
    const startTime = Date.now();
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Should load within 2 seconds
    expect(loadTime).toBeLessThan(2000);
  });

  test('Progress tracking updates in real-time', async ({ page }) => {
    await loginAs(page, testUsers.viewer);
    await navigateToCourseContent(page);

    await page.click('text=My Courses');
    await page.click('text=View Course');
    await page.click('text=Video Content');

    // Start video and check for real-time updates
    await page.click('button:has-text("Play")');
    
    // Progress should update automatically
    await expect(page.locator('text=Progress: 0%')).toBeVisible();
    
    // Simulate progress
    await page.waitForTimeout(1000);
    await expect(page.locator('text=Progress: 25%')).toBeVisible();
  });
});

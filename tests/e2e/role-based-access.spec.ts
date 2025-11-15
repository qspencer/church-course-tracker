import { test, expect, type Page, type TestInfo } from '@playwright/test';
import { loginAsRole } from './utils/auth';

type UserRole = 'admin' | 'staff' | 'viewer';

// Helper function to login with specific role
async function loginAs(page: Page, role: UserRole, testInfo: TestInfo) {
  return loginAsRole(page, role, testInfo);
}

// Helper function to check if element is visible
async function isVisible(page: Page, selector: string): Promise<boolean> {
  try {
    await page.waitForSelector(selector, { timeout: 1000 });
    return await page.isVisible(selector);
  } catch {
    return false;
  }
}

test.describe('Role-Based Access Control', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('https://apps.quentinspencer.com/churchcoursetracker');
  });

  test.describe('Admin Role Tests', () => {
    test('Admin can access all system features', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }

      // Check dashboard access
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
      
      // Admin should see all navigation items
      const adminNavItems = [
        'Courses',
        'Users', 
        'Audit Logs',
        'System Settings',
        'Reports'
      ];

      for (const item of adminNavItems) {
        await expect(page.locator(`text=${item}`)).toBeVisible();
      }
    });

    test('Admin can manage users', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }

      // Navigate to users page
      await page.click('text=Users');
      await page.waitForURL('**/users');

      // Should be able to see user management interface
      await expect(page.locator('text=User Management')).toBeVisible();
      await expect(page.locator('button:has-text("Add User")')).toBeVisible();
      await expect(page.locator('button:has-text("Edit User")')).toBeVisible();
    });

    test('Admin can access audit logs', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }

      // Navigate to audit logs
      await page.click('text=Audit Logs');
      await page.waitForURL('**/audit');

      // Should see audit log interface
      await expect(page.locator('text=System Audit Logs')).toBeVisible();
      await expect(page.locator('button:has-text("Export Logs")')).toBeVisible();
      await expect(page.locator('button:has-text("Filter Logs")')).toBeVisible();
    });

    test('Admin can delete courses', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }

      // Navigate to courses
      await page.click('text=Courses');
      await page.waitForURL('**/courses');

      // Should see delete buttons for courses
      const deleteButtons = page.locator('button:has-text("Delete")');
      await expect(deleteButtons.first()).toBeVisible();
    });

    test('Admin can access system settings', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }

      // Navigate to system settings
      await page.click('text=System Settings');
      await page.waitForURL('**/settings');

      // Should see system configuration options
      await expect(page.locator('text=System Configuration')).toBeVisible();
      await expect(page.locator('text=Planning Center Integration')).toBeVisible();
    });
  });

  test.describe('Staff Role Tests', () => {
    test('Staff can access operational features', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }

      // Check dashboard access
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
      
      // Staff should see operational navigation items
      const staffNavItems = [
        'Courses',
        'Content Management',
        'Progress Reports',
        'User Support'
      ];

      for (const item of staffNavItems) {
        await expect(page.locator(`text=${item}`)).toBeVisible();
      }

      // Staff should NOT see admin-only items
      await expect(page.locator('text=Audit Logs')).not.toBeVisible();
      await expect(page.locator('text=System Settings')).not.toBeVisible();
    });

    test('Staff can manage courses and content', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }

      // Navigate to courses
      await page.click('text=Courses');
      await page.waitForURL('**/courses');

      // Should be able to create and edit courses
      await expect(page.locator('button:has-text("Create Course")')).toBeVisible();
      await expect(page.locator('button:has-text("Edit Course")')).toBeVisible();
      
      // Should NOT see delete buttons
      await expect(page.locator('button:has-text("Delete")')).not.toBeVisible();
    });

    test('Staff can upload course content', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }

      // Navigate to content management
      await page.click('text=Content Management');
      await page.waitForURL('**/content');

      // Should see file upload interface
      await expect(page.locator('input[type="file"]')).toBeVisible();
      await expect(page.locator('button:has-text("Upload File")')).toBeVisible();
    });

    test('Staff can view progress reports', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }

      // Navigate to progress reports
      await page.click('text=Progress Reports');
      await page.waitForURL('**/reports');

      // Should see reporting interface
      await expect(page.locator('text=Student Progress')).toBeVisible();
      await expect(page.locator('text=Course Analytics')).toBeVisible();
    });

    test('Staff cannot access admin features', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }

      // Try to access admin URLs directly
      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/admin');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');

      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/audit');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
    });
  });

  test.describe('Viewer Role Tests', () => {
    test('Viewer can access limited features', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }

      // Check dashboard access
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
      
      // Viewer should see limited navigation items
      const viewerNavItems = [
        'My Courses',
        'Progress',
        'Profile'
      ];

      for (const item of viewerNavItems) {
        await expect(page.locator(`text=${item}`)).toBeVisible();
      }

      // Viewer should NOT see management items
      await expect(page.locator('text=User Management')).not.toBeVisible();
      await expect(page.locator('text=Content Management')).not.toBeVisible();
      await expect(page.locator('text=Audit Logs')).not.toBeVisible();
    });

    test('Viewer can view and enroll in courses', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }

      // Navigate to courses
      await page.click('text=My Courses');
      await page.waitForURL('**/courses');

      // Should see course listings
      await expect(page.locator('text=Available Courses')).toBeVisible();
      await expect(page.locator('button:has-text("Enroll")')).toBeVisible();
      
      // Should NOT see management buttons
      await expect(page.locator('button:has-text("Create Course")')).not.toBeVisible();
      await expect(page.locator('button:has-text("Edit Course")')).not.toBeVisible();
    });

    test('Viewer can track personal progress', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }

      // Navigate to progress
      await page.click('text=Progress');
      await page.waitForURL('**/progress');

      // Should see personal progress interface
      await expect(page.locator('text=My Progress')).toBeVisible();
      await expect(page.locator('text=Completed Courses')).toBeVisible();
    });

    test('Viewer can manage profile', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }

      // Navigate to profile
      await page.click('text=Profile');
      await page.waitForURL('**/profile');

      // Should see profile management interface
      await expect(page.locator('text=Profile Settings')).toBeVisible();
      await expect(page.locator('input[name="full_name"]')).toBeVisible();
      await expect(page.locator('input[name="email"]')).toBeVisible();
    });

    test('Viewer cannot access management features', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }

      // Try to access management URLs directly
      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/users');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');

      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/content');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
    });
  });

  test.describe('Cross-Role Security Tests', () => {
    test('Users cannot access other roles features', async ({ page }, testInfo) => {
      // Test staff cannot access admin features
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }
      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/audit');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');

      // Test viewer cannot access staff features
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }
      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/content');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
    });

    test('API endpoints respect role permissions', async ({ page }, testInfo) => {
      // Test admin API access
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }
      const adminResponse = await page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/audit/');
      expect(adminResponse.status()).toBe(200);

      // Test staff API access (should be denied for audit)
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }
      const staffResponse = await page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/audit/');
      expect(staffResponse.status()).toBe(403);

      // Test viewer API access (should be denied for audit)
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }
      const viewerResponse = await page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/audit/');
      expect(viewerResponse.status()).toBe(403);
    });
  });

  test.describe('Role-Specific Workflows', () => {
    test('Admin course management workflow', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }

      // Create course
      await page.click('text=Courses');
      await page.click('button:has-text("Create Course")');
      await page.fill('input[name="title"]', 'Test Admin Course');
      await page.fill('textarea[name="description"]', 'Course created by admin');
      await page.click('button:has-text("Save")');

      // Verify course creation
      await expect(page.locator('text=Test Admin Course')).toBeVisible();

      // Delete course (admin-only capability)
      await page.click('button:has-text("Delete")');
      await page.click('button:has-text("Confirm Delete")');
      await expect(page.locator('text=Test Admin Course')).not.toBeVisible();
    });

    test('Staff content management workflow', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'staff', testInfo))) {
        return;
      }

      // Navigate to content management
      await page.click('text=Content Management');
      
      // Upload file
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'test-document.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('test content')
      });
      
      await page.click('button:has-text("Upload File")');
      await expect(page.locator('text=File uploaded successfully')).toBeVisible();
    });

    test('Viewer course enrollment workflow', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'viewer', testInfo))) {
        return;
      }

      // Browse courses
      await page.click('text=My Courses');
      await expect(page.locator('text=Available Courses')).toBeVisible();

      // Enroll in course
      await page.click('button:has-text("Enroll")');
      await expect(page.locator('text=Successfully enrolled')).toBeVisible();

      // View progress
      await page.click('text=Progress');
      await expect(page.locator('text=My Progress')).toBeVisible();
    });
  });

  test.describe('Error Handling and Security', () => {
    test('Unauthorized access redirects to login', async ({ page }) => {
      // Try to access protected page without login
      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/auth');
    });

    test('Invalid credentials show error message', async ({ page }) => {
      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/auth');
   await page.waitForTimeout(2000); // Wait for Angular to initialize
      await page.fill('input[formControlName="username"]', 'invalid');
      await page.fill('input[formControlName="password"]', 'invalid');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
    });

    test('Session timeout redirects to login', async ({ page }, testInfo) => {
      if (!(await loginAs(page, 'admin', testInfo))) {
        return;
      }
      
      // Simulate session timeout by clearing cookies
      await page.context().clearCookies();
      
      // Try to access protected page
      await page.goto('https://apps.quentinspencer.com/churchcoursetracker/dashboard');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/churchcoursetracker/auth');
    });
  });
});

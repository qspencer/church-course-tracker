import { test, expect, Page } from '@playwright/test';

// Test data
const testUsers = {
  admin: { username: 'admin', password: 'admin123' },
  staff: { username: 'staff', password: 'staff123' },
  viewer: { username: 'viewer', password: 'viewer123' }
};

async function loginAs(page: Page, user: typeof testUsers.admin) {
  await page.goto('https://apps.quentinspencer.com/auth');
  await page.fill('input[name="username"]', user.username);
  await page.fill('input[name="password"]', user.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('https://apps.quentinspencer.com/dashboard');
}

test.describe('Course Management Tests', () => {
  test.describe('Admin Course Management', () => {
    test('Admin can create, update, and delete courses', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      // Create course
      await page.click('text=Courses');
      await page.click('button:has-text("Create Course")');
      
      await page.fill('input[name="title"]', 'Advanced Bible Study');
      await page.fill('textarea[name="description"]', 'In-depth study of biblical texts');
      await page.fill('input[name="duration_weeks"]', '12');
      await page.fill('input[name="max_capacity"]', '25');
      
      await page.click('button:has-text("Save")');
      await expect(page.locator('text=Course created successfully')).toBeVisible();

      // Update course
      await page.click('button:has-text("Edit")');
      await page.fill('input[name="title"]', 'Advanced Bible Study - Updated');
      await page.click('button:has-text("Update")');
      await expect(page.locator('text=Course updated successfully')).toBeVisible();

      // Delete course (admin-only)
      await page.click('button:has-text("Delete")');
      await page.click('button:has-text("Confirm Delete")');
      await expect(page.locator('text=Course deleted successfully')).toBeVisible();
    });

    test('Admin can manage course prerequisites', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Courses');
      await page.click('button:has-text("Create Course")');
      
      await page.fill('input[name="title"]', 'Advanced Course');
      await page.selectOption('select[name="prerequisites"]', 'Basic Course');
      
      await page.click('button:has-text("Save")');
      await expect(page.locator('text=Prerequisites set successfully')).toBeVisible();
    });
  });

  test.describe('Staff Course Management', () => {
    test('Staff can create and update courses but not delete', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      // Create course
      await page.click('text=Courses');
      await page.click('button:has-text("Create Course")');
      
      await page.fill('input[name="title"]', 'Staff Created Course');
      await page.fill('textarea[name="description"]', 'Course created by staff member');
      await page.click('button:has-text("Save")');
      await expect(page.locator('text=Course created successfully')).toBeVisible();

      // Update course
      await page.click('button:has-text("Edit")');
      await page.fill('input[name="title"]', 'Staff Created Course - Updated');
      await page.click('button:has-text("Update")');
      await expect(page.locator('text=Course updated successfully')).toBeVisible();

      // Should NOT see delete button
      await expect(page.locator('button:has-text("Delete")')).not.toBeVisible();
    });

    test('Staff can manage course content', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      await page.click('text=Courses');
      await page.click('text=Course Content');
      
      // Add module
      await page.click('button:has-text("Add Module")');
      await page.fill('input[name="title"]', 'Introduction Module');
      await page.fill('textarea[name="description"]', 'Course introduction');
      await page.click('button:has-text("Save Module")');
      await expect(page.locator('text=Module added successfully')).toBeVisible();

      // Upload content
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'lesson1.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('test content')
      });
      await page.click('button:has-text("Upload")');
      await expect(page.locator('text=File uploaded successfully')).toBeVisible();
    });
  });

  test.describe('Viewer Course Access', () => {
    test('Viewer can browse and enroll in courses', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=My Courses');
      
      // Browse available courses
      await expect(page.locator('text=Available Courses')).toBeVisible();
      await expect(page.locator('text=Course Catalog')).toBeVisible();

      // Enroll in course
      await page.click('button:has-text("Enroll")');
      await expect(page.locator('text=Successfully enrolled')).toBeVisible();

      // View enrolled courses
      await page.click('text=My Enrolled Courses');
      await expect(page.locator('text=Enrolled Courses')).toBeVisible();
    });

    test('Viewer can access course content', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=My Courses');
      await page.click('text=View Course');
      
      // Access course modules
      await expect(page.locator('text=Course Modules')).toBeVisible();
      await page.click('text=Module 1');
      
      // View content
      await expect(page.locator('text=Course Content')).toBeVisible();
      await page.click('text=Download Material');
      await expect(page.locator('text=Download started')).toBeVisible();
    });

    test('Viewer cannot access management features', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      // Should not see management buttons
      await expect(page.locator('button:has-text("Create Course")')).not.toBeVisible();
      await expect(page.locator('button:has-text("Edit Course")')).not.toBeVisible();
      await expect(page.locator('button:has-text("Delete Course")')).not.toBeVisible();
    });
  });
});

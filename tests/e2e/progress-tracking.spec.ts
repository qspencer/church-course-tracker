import { test, expect, Page } from '@playwright/test';

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

test.describe('Progress Tracking Tests', () => {
  test.describe('Admin Progress Monitoring', () => {
    test('Admin can view all user progress', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Progress Reports');
      
      // Should see comprehensive progress dashboard
      await expect(page.locator('text=System Progress Dashboard')).toBeVisible();
      await expect(page.locator('text=All Users Progress')).toBeVisible();
      await expect(page.locator('text=Course Completion Rates')).toBeVisible();
      
      // Should see progress charts and statistics
      await expect(page.locator('canvas[data-chart="progress"]')).toBeVisible();
      await expect(page.locator('text=Completion Statistics')).toBeVisible();
    });

    test('Admin can generate progress reports', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Progress Reports');
      await page.click('button:has-text("Generate Report")');
      
      // Should see report generation options
      await expect(page.locator('text=Report Options')).toBeVisible();
      await expect(page.locator('input[name="date_range"]')).toBeVisible();
      await expect(page.locator('select[name="course_filter"]')).toBeVisible();
      
      // Generate report
      await page.selectOption('select[name="course_filter"]', 'all');
      await page.click('button:has-text("Generate")');
      await expect(page.locator('text=Report generated successfully')).toBeVisible();
    });

    test('Admin can export progress data', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Progress Reports');
      await page.click('button:has-text("Export Data")');
      
      // Should see export options
      await expect(page.locator('text=Export Options')).toBeVisible();
      await expect(page.locator('button:has-text("Export CSV")')).toBeVisible();
      await expect(page.locator('button:has-text("Export Excel")')).toBeVisible();
    });
  });

  test.describe('Staff Progress Monitoring', () => {
    test('Staff can view course progress', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      await page.click('text=Progress Reports');
      
      // Should see course-focused progress dashboard
      await expect(page.locator('text=Course Progress Dashboard')).toBeVisible();
      await expect(page.locator('text=Student Progress')).toBeVisible();
      await expect(page.locator('text=Course Analytics')).toBeVisible();
    });

    test('Staff can monitor individual student progress', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      await page.click('text=Progress Reports');
      await page.click('text=Student Progress');
      
      // Should see student list and progress
      await expect(page.locator('text=Student List')).toBeVisible();
      await expect(page.locator('tr[data-student]')).toHaveCount.greaterThan(0);
      
      // Click on a student to view detailed progress
      await page.click('tr[data-student] >> first');
      await expect(page.locator('text=Student Progress Details')).toBeVisible();
    });

    test('Staff can track content access', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      await page.click('text=Progress Reports');
      await page.click('text=Content Access');
      
      // Should see content access analytics
      await expect(page.locator('text=Content Access Analytics')).toBeVisible();
      await expect(page.locator('text=Most Accessed Content')).toBeVisible();
      await expect(page.locator('text=Least Accessed Content')).toBeVisible();
    });

    test('Staff can identify students needing support', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      await page.click('text=Progress Reports');
      await page.click('text=Students Needing Support');
      
      // Should see students with low progress
      await expect(page.locator('text=Students Needing Support')).toBeVisible();
      await expect(page.locator('text=Low Progress Students')).toBeVisible();
      await expect(page.locator('text=At-Risk Students')).toBeVisible();
    });
  });

  test.describe('Viewer Personal Progress', () => {
    test('Viewer can view personal progress', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=Progress');
      
      // Should see personal progress dashboard
      await expect(page.locator('text=My Progress')).toBeVisible();
      await expect(page.locator('text=Completed Courses')).toBeVisible();
      await expect(page.locator('text=In Progress')).toBeVisible();
    });

    test('Viewer can track course completion', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=Progress');
      await page.click('text=Course Progress');
      
      // Should see course progress details
      await expect(page.locator('text=Course Progress Details')).toBeVisible();
      await expect(page.locator('text=Completion Percentage')).toBeVisible();
      await expect(page.locator('text=Time Spent')).toBeVisible();
    });

    test('Viewer can view learning history', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=Progress');
      await page.click('text=Learning History');
      
      // Should see learning history
      await expect(page.locator('text=Learning History')).toBeVisible();
      await expect(page.locator('text=Completed Courses')).toBeVisible();
      await expect(page.locator('text=Certificates Earned')).toBeVisible();
    });

    test('Viewer can set learning goals', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=Progress');
      await page.click('text=Learning Goals');
      
      // Should see goal setting interface
      await expect(page.locator('text=Set Learning Goals')).toBeVisible();
      await page.fill('input[name="goal_description"]', 'Complete 5 courses this month');
      await page.selectOption('select[name="goal_type"]', 'completion');
      await page.fill('input[name="target_date"]', '2024-12-31');
      
      await page.click('button:has-text("Set Goal")');
      await expect(page.locator('text=Goal set successfully')).toBeVisible();
    });
  });

  test.describe('Progress Analytics', () => {
    test('Progress charts display correctly', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Progress Reports');
      
      // Check for progress charts
      await expect(page.locator('canvas[data-chart="completion"]')).toBeVisible();
      await expect(page.locator('canvas[data-chart="engagement"]')).toBeVisible();
      await expect(page.locator('canvas[data-chart="time-spent"]')).toBeVisible();
    });

    test('Progress statistics are accurate', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Progress Reports');
      
      // Check for key statistics
      await expect(page.locator('text=Total Students')).toBeVisible();
      await expect(page.locator('text=Active Students')).toBeVisible();
      await expect(page.locator('text=Completion Rate')).toBeVisible();
      await expect(page.locator('text=Average Progress')).toBeVisible();
    });

    test('Progress filtering works', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Progress Reports');
      
      // Test date range filtering
      await page.fill('input[name="start_date"]', '2024-01-01');
      await page.fill('input[name="end_date"]', '2024-12-31');
      await page.click('button:has-text("Filter")');
      
      await expect(page.locator('text=Filtered Results')).toBeVisible();
      
      // Test course filtering
      await page.selectOption('select[name="course_filter"]', 'Bible Study');
      await page.click('button:has-text("Filter")');
      
      await expect(page.locator('text=Filtered by course')).toBeVisible();
    });
  });

  test.describe('Progress Notifications', () => {
    test('Progress notifications are sent', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      // Complete a course module
      await page.click('text=My Courses');
      await page.click('text=View Course');
      await page.click('text=Complete Module');
      
      // Should see progress notification
      await expect(page.locator('text=Progress updated')).toBeVisible();
    });

    test('Achievement notifications work', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      // Complete a course
      await page.click('text=My Courses');
      await page.click('text=Complete Course');
      
      // Should see achievement notification
      await expect(page.locator('text=Course completed!')).toBeVisible();
      await expect(page.locator('text=Certificate earned')).toBeVisible();
    });
  });
});

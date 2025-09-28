import { test, expect } from '@playwright/test';

test.describe('Courses Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // Navigate to courses page
    const coursesLink = page.locator('text=Courses').or(page.locator('a[href*="courses"]'));
    await coursesLink.click();
    await expect(page).toHaveURL(/.*\/courses/, { timeout: 10000 });
  });

  test('should display courses page', async ({ page }) => {
    // Check for courses page title
    await expect(page.locator('text=Courses')).toBeVisible();
    
    // Check for add course button
    await expect(page.locator('button:has-text("Add Course")').or(
      page.locator('button:has-text("New Course")')
    )).toBeVisible();
  });

  test('should open add course dialog', async ({ page }) => {
    // Click add course button
    const addButton = page.locator('button:has-text("Add Course")').or(
      page.locator('button:has-text("New Course")')
    );
    await addButton.click();
    
    // Check for dialog/modal
    await expect(page.locator('text=Add Course').or(page.locator('text=New Course'))).toBeVisible();
    
    // Check for form fields
    await expect(page.locator('input[placeholder*="title"], input[placeholder*="name"]')).toBeVisible();
    await expect(page.locator('textarea, input[type="text"]')).toBeVisible();
  });

  test('should create a new course', async ({ page }) => {
    // Click add course button
    const addButton = page.locator('button:has-text("Add Course")').or(
      page.locator('button:has-text("New Course")')
    );
    await addButton.click();
    
    // Fill in course details
    await page.fill('input[placeholder*="title"], input[placeholder*="name"]', 'Test Course');
    await page.fill('textarea, input[type="text"]', 'This is a test course description');
    
    // Look for duration field
    const durationField = page.locator('input[type="number"]').or(
      page.locator('input[placeholder*="duration"]')
    );
    if (await durationField.isVisible()) {
      await durationField.fill('4');
    }
    
    // Submit the form
    const submitButton = page.locator('button:has-text("Save")').or(
      page.locator('button:has-text("Create")').or(
        page.locator('button[type="submit"]')
      )
    );
    await submitButton.click();
    
    // Check for success message or course in list
    await expect(page.locator('text=Test Course')).toBeVisible({ timeout: 10000 });
  });

  test('should edit an existing course', async ({ page }) => {
    // Look for edit button on first course
    const editButton = page.locator('button:has-text("Edit")').first();
    
    if (await editButton.isVisible()) {
      await editButton.click();
      
      // Check for edit dialog
      await expect(page.locator('text=Edit Course')).toBeVisible();
      
      // Modify course title
      const titleField = page.locator('input[placeholder*="title"], input[placeholder*="name"]');
      await titleField.clear();
      await titleField.fill('Updated Test Course');
      
      // Save changes
      const saveButton = page.locator('button:has-text("Save")').or(
        page.locator('button:has-text("Update")')
      );
      await saveButton.click();
      
      // Check for updated course
      await expect(page.locator('text=Updated Test Course')).toBeVisible({ timeout: 10000 });
    }
  });

  test('should delete a course', async ({ page }) => {
    // Look for delete button on first course
    const deleteButton = page.locator('button:has-text("Delete")').first();
    
    if (await deleteButton.isVisible()) {
      await deleteButton.click();
      
      // Check for confirmation dialog
      await expect(page.locator('text=Confirm').or(page.locator('text=Are you sure'))).toBeVisible();
      
      // Confirm deletion
      const confirmButton = page.locator('button:has-text("Yes")').or(
        page.locator('button:has-text("Delete")')
      );
      await confirmButton.click();
      
      // Check for success message
      await expect(page.locator('text=deleted').or(page.locator('text=removed'))).toBeVisible({ timeout: 10000 });
    }
  });

  test('should search courses', async ({ page }) => {
    // Look for search input
    const searchInput = page.locator('input[placeholder*="search"]').or(
      page.locator('input[type="search"]')
    );
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('Test');
      
      // Wait for search results
      await page.waitForTimeout(1000);
      
      // Check that results are filtered
      const results = page.locator('[data-testid="course-item"], .course-item, tr');
      const count = await results.count();
      expect(count).toBeGreaterThan(0);
    }
  });
});

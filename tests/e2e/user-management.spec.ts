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

test.describe('User Management Tests', () => {
  test.describe('Admin User Management', () => {
    test('Admin can create new users', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Users');
      await page.click('button:has-text("Add User")');
      
      // Fill user form
      await page.fill('input[name="username"]', 'newuser');
      await page.fill('input[name="email"]', 'newuser@example.com');
      await page.fill('input[name="full_name"]', 'New User');
      await page.fill('input[name="password"]', 'password123');
      await page.selectOption('select[name="role"]', 'staff');
      
      await page.click('button:has-text("Create User")');
      await expect(page.locator('text=User created successfully')).toBeVisible();
    });

    test('Admin can update user roles', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Users');
      await page.click('button:has-text("Edit User")');
      
      // Change role
      await page.selectOption('select[name="role"]', 'admin');
      await page.click('button:has-text("Update User")');
      await expect(page.locator('text=User role updated successfully')).toBeVisible();
    });

    test('Admin can deactivate users', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Users');
      await page.click('button:has-text("Deactivate User")');
      await page.click('button:has-text("Confirm Deactivation")');
      await expect(page.locator('text=User deactivated successfully')).toBeVisible();
    });

    test('Admin can reset user passwords', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Users');
      await page.click('button:has-text("Reset Password")');
      await page.fill('input[name="new_password"]', 'newpassword123');
      await page.click('button:has-text("Reset")');
      await expect(page.locator('text=Password reset successfully')).toBeVisible();
    });
  });

  test.describe('Staff User Support', () => {
    test('Staff can view user information but not modify', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      // Staff should not see user management
      await expect(page.locator('text=Users')).not.toBeVisible();
      
      // Try to access user management directly
      await page.goto('https://apps.quentinspencer.com/users');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/dashboard');
    });

    test('Staff can provide user support', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      await page.click('text=User Support');
      
      // Should see support interface
      await expect(page.locator('text=Support Dashboard')).toBeVisible();
      await expect(page.locator('text=Active Support Tickets')).toBeVisible();
      
      // Create support ticket
      await page.click('button:has-text("New Ticket")');
      await page.fill('input[name="subject"]', 'User needs help with course access');
      await page.fill('textarea[name="description"]', 'User cannot access course content');
      await page.click('button:has-text("Create Ticket")');
      await expect(page.locator('text=Ticket created successfully')).toBeVisible();
    });
  });

  test.describe('Viewer Profile Management', () => {
    test('Viewer can update personal profile', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=Profile');
      
      // Update profile information
      await page.fill('input[name="full_name"]', 'Updated Name');
      await page.fill('input[name="email"]', 'updated@example.com');
      await page.fill('input[name="phone"]', '123-456-7890');
      
      await page.click('button:has-text("Update Profile")');
      await expect(page.locator('text=Profile updated successfully')).toBeVisible();
    });

    test('Viewer can change password', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=Profile');
      await page.click('text=Change Password');
      
      await page.fill('input[name="current_password"]', 'viewer123');
      await page.fill('input[name="new_password"]', 'newpassword123');
      await page.fill('input[name="confirm_password"]', 'newpassword123');
      
      await page.click('button:has-text("Change Password")');
      await expect(page.locator('text=Password changed successfully')).toBeVisible();
    });

    test('Viewer can manage notification preferences', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      await page.click('text=Profile');
      await page.click('text=Notifications');
      
      // Toggle notification preferences
      await page.check('input[name="email_notifications"]');
      await page.check('input[name="course_updates"]');
      await page.uncheck('input[name="system_announcements"]');
      
      await page.click('button:has-text("Save Preferences")');
      await expect(page.locator('text=Preferences saved successfully')).toBeVisible();
    });
  });
});

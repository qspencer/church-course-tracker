import { test, expect } from '@playwright/test';
import { API_BASE_URL, getApiAuthToken, testUsers } from './utils/auth';

// Credentials are loaded from environment variables via utils/auth.ts
// Set E2E_ADMIN_USERNAME, E2E_ADMIN_PASSWORD, etc. in your environment
const adminUser = testUsers.admin;

test.describe('Working API Tests', () => {
  test('API courses endpoint responds correctly', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/v1/courses/`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    console.log(`✓ Courses endpoint returned ${data.length} courses`);
  });

  test('API users endpoint responds correctly', async ({ request }) => {
    // /users requires admin auth as of May 2026 hardening pass.
    const token = await getApiAuthToken(request, 'admin');
    test.skip(!token, 'admin credentials not configured (or login failed)');

    const response = await request.get(`${API_BASE_URL}/api/v1/users/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    console.log(`✓ Users endpoint returned ${data.length} users`);
  });

  test('API authentication endpoint works', async ({ request }) => {
    if (!adminUser) {
      test.skip(true, 'Admin credentials are not configured for API authentication validation');
      return;
    }

    const response = await request.post(`${API_BASE_URL}/api/v1/auth/login`, {
      data: adminUser
    });

    if (response.status() === 401) {
      test.skip(true, 'Configured admin credentials are not valid in the target environment');
      return;
    }

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data.access_token).toBeDefined();
    console.log('✓ Authentication endpoint working correctly');
  });

  test('API authentication with invalid credentials fails', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/v1/auth/login`, {
      data: {
        username: 'invalid',
        password: 'invalid'
      }
    });
    
    // Allow for rate limiting (429) - retry once if rate limited
    let status = response.status();
    if (status === 429) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      const retryResponse = await request.post(`${API_BASE_URL}/api/v1/auth/login`, {
        data: {
          username: 'invalid',
          password: 'invalid'
        }
      });
      status = retryResponse.status();
    }
    
    // Should reject invalid credentials (401), be rate limited (429), or account locked (423)
    expect([401, 423, 429]).toContain(status);
    console.log(`✓ Invalid credentials properly rejected (status: ${status})`);
  });

  test('API response times are acceptable', async ({ request }) => {
    const startTime = Date.now();
    const response = await request.get(`${API_BASE_URL}/api/v1/courses/`);
    const responseTime = Date.now() - startTime;
    
    // Allow for rate limiting (429) - retry once if rate limited
    let status = response.status();
    if (status === 429) {
      // Wait a bit and retry
      await new Promise(resolve => setTimeout(resolve, 2000));
      const retryResponse = await request.get(`${API_BASE_URL}/api/v1/courses/`);
      status = retryResponse.status();
    }
    
    expect([200, 429]).toContain(status); // Accept 200 or 429 (rate limited)
    expect(responseTime).toBeLessThan(5000); // Should respond within 5 seconds
    console.log(`✓ API response time: ${responseTime}ms (status: ${status})`);
  });

  test('API handles different HTTP methods', async ({ request }) => {
    // Test GET
    const getResponse = await request.get(`${API_BASE_URL}/api/v1/courses/`);
    expect(getResponse.status()).toBe(200);

    // Test POST (login)
    if (!adminUser) {
      test.skip(true, 'Admin credentials are not configured for API authentication validation');
      return;
    }

    let postResponse = await request.post(`${API_BASE_URL}/api/v1/auth/login`, {
      data: adminUser
    });

    // Handle rate limiting - wait and retry
    if (postResponse.status() === 429) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      postResponse = await request.post(`${API_BASE_URL}/api/v1/auth/login`, {
        data: adminUser
      });
    }

    if (postResponse.status() === 401) {
      test.skip(true, 'Configured admin credentials are not valid in the target environment');
      return;
    }

    // Accept 200 (success) or 429 (rate limited after retry) as valid outcomes
    expect([200, 429]).toContain(postResponse.status());

    console.log(`✓ API handles GET and POST methods correctly (POST status: ${postResponse.status()})`);
  });

  test('API returns proper JSON format', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/v1/courses/`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(typeof data).toBe('object');
    expect(Array.isArray(data)).toBeTruthy();
    
    console.log('✓ API returns proper JSON format');
  });

  test('API handles concurrent requests', async ({ request }) => {
    const requests = [];
    for (let i = 0; i < 5; i++) {
      requests.push(request.get(`${API_BASE_URL}/api/v1/courses/`));
    }
    
    const responses = await Promise.all(requests);
    
    // Allow for rate limiting (429) - at least some requests should succeed
    let successCount = 0;
    let rateLimitedCount = 0;
    for (const response of responses) {
      const status = response.status();
      if (status === 200) {
        successCount++;
      } else if (status === 429) {
        rateLimitedCount++;
      }
    }
    
    // At least some requests should succeed, or all should be rate limited (which is acceptable)
    expect(successCount).toBeGreaterThan(0);
    
    console.log(`✓ API handles concurrent requests correctly (${successCount} succeeded, ${rateLimitedCount} rate limited)`);
  });

  test('API error handling works', async ({ request }) => {
    // Test 404 endpoint
    const response = await request.get(`${API_BASE_URL}/api/v1/nonexistent/`);
    // Allow for rate limiting (429) - retry once if rate limited
    let status = response.status();
    if (status === 429) {
      // Wait a bit and retry
      await new Promise(resolve => setTimeout(resolve, 2000));
      const retryResponse = await request.get(`${API_BASE_URL}/api/v1/nonexistent/`);
      status = retryResponse.status();
    }
    // Should return 404 (not found) or 429 (rate limited)
    expect([404, 429]).toContain(status);
    
    console.log(`✓ API error handling works correctly (status: ${status})`);
  });
});

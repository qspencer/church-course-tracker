import { test, expect } from '@playwright/test';

test.describe('Working API Tests', () => {
  test('API courses endpoint responds correctly', async ({ request }) => {
    const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    console.log(`✓ Courses endpoint returned ${data.length} courses`);
  });

  test('API users endpoint responds correctly', async ({ request }) => {
    const response = await request.get('https://api.quentinspencer.com/api/v1/users/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    console.log(`✓ Users endpoint returned ${data.length} users`);
  });

  test('API authentication endpoint works', async ({ request }) => {
    const response = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.access_token).toBeDefined();
    console.log('✓ Authentication endpoint working correctly');
  });

  test('API authentication with invalid credentials fails', async ({ request }) => {
    const response = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
      data: {
        username: 'invalid',
        password: 'invalid'
      }
    });
    
    expect(response.status()).toBe(401);
    console.log('✓ Invalid credentials properly rejected');
  });

  test('API response times are acceptable', async ({ request }) => {
    const startTime = Date.now();
    const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    const responseTime = Date.now() - startTime;
    
    expect(response.status()).toBe(200);
    expect(responseTime).toBeLessThan(5000); // Should respond within 5 seconds
    console.log(`✓ API response time: ${responseTime}ms`);
  });

  test('API handles different HTTP methods', async ({ request }) => {
    // Test GET
    const getResponse = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    expect(getResponse.status()).toBe(200);
    
    // Test POST (login)
    const postResponse = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
      data: { username: 'admin', password: 'admin123' }
    });
    expect(postResponse.status()).toBe(200);
    
    console.log('✓ API handles GET and POST methods correctly');
  });

  test('API returns proper JSON format', async ({ request }) => {
    const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(typeof data).toBe('object');
    expect(Array.isArray(data)).toBeTruthy();
    
    console.log('✓ API returns proper JSON format');
  });

  test('API handles concurrent requests', async ({ request }) => {
    const requests = [];
    for (let i = 0; i < 5; i++) {
      requests.push(request.get('https://api.quentinspencer.com/api/v1/courses/'));
    }
    
    const responses = await Promise.all(requests);
    
    for (const response of responses) {
      expect(response.status()).toBe(200);
    }
    
    console.log('✓ API handles concurrent requests correctly');
  });

  test('API error handling works', async ({ request }) => {
    // Test 404 endpoint
    const response = await request.get('https://api.quentinspencer.com/api/v1/nonexistent/');
    expect(response.status()).toBe(404);
    
    console.log('✓ API error handling works correctly');
  });
});

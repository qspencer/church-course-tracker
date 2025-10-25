import { test, expect } from '@playwright/test';

test.describe('API Endpoint Tests', () => {
  test('API health endpoint is accessible', async ({ request }) => {
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('API courses endpoint responds', async ({ request }) => {
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/courses/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });

  test('API users endpoint responds', async ({ request }) => {
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/users/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });

  test('API authentication endpoint works', async ({ request }) => {
    const response = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.access_token).toBeDefined();
  });

  test('API CORS headers are present', async ({ request }) => {
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/health');
    const headers = response.headers();
    
    expect(headers['access-control-allow-origin']).toBeDefined();
    expect(headers['access-control-allow-methods']).toBeDefined();
    expect(headers['access-control-allow-headers']).toBeDefined();
  });

  test('API rate limiting works', async ({ request }) => {
    // Make multiple rapid requests to test rate limiting
    const requests = [];
    for (let i = 0; i < 10; i++) {
      requests.push(request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/health'));
    }
    
    const responses = await Promise.all(requests);
    const rateLimitedResponses = responses.filter(r => r.status() === 429);
    
    // At least one request should be rate limited
    expect(rateLimitedResponses.length).toBeGreaterThan(0);
  });

  test('API security headers are present', async ({ request }) => {
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/health');
    const headers = response.headers();
    
    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['x-frame-options']).toBe('DENY');
    expect(headers['x-xss-protection']).toBe('1; mode=block');
  });
});

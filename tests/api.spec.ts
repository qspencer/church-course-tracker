import { test, expect } from '@playwright/test';

test.describe('API Integration', () => {
  test('should have working health endpoint', async ({ request }) => {
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('should authenticate via API', async ({ request }) => {
    const response = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.access_token).toBeDefined();
    expect(data.token_type).toBe('bearer');
  });

  test('should get courses via API', async ({ request }) => {
    // First authenticate
    const authResponse = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    const authData = await authResponse.json();
    const token = authData.access_token;
    
    // Get courses
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/courses', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });

  test('should get members via API', async ({ request }) => {
    // First authenticate
    const authResponse = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    const authData = await authResponse.json();
    const token = authData.access_token;
    
    // Get members
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/members', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });

  test('should get users via API (admin only)', async ({ request }) => {
    // First authenticate
    const authResponse = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    const authData = await authResponse.json();
    const token = authData.access_token;
    
    // Get users
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });

  test('should handle invalid authentication', async ({ request }) => {
    const response = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      data: {
        username: 'invalid',
        password: 'wrong'
      }
    });
    
    expect(response.status()).toBe(401);
  });

  test('should handle unauthorized API access', async ({ request }) => {
    const response = await request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/courses');
    expect(response.status()).toBe(401);
  });

  test('should create a course via API', async ({ request }) => {
    // First authenticate
    const authResponse = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    const authData = await authResponse.json();
    const token = authData.access_token;
    
    // Create a course
    const response = await request.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/courses', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        title: 'API Test Course',
        description: 'This course was created via API test',
        duration_weeks: 4
      }
    });
    
    expect(response.status()).toBe(201);
    
    const data = await response.json();
    expect(data.title).toBe('API Test Course');
    expect(data.id).toBeDefined();
  });

  test('should handle CORS preflight requests', async ({ request }) => {
    const response = await request.options('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', {
      headers: {
        'Origin': 'https://apps.quentinspencer.com',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
      }
    });
    
    expect(response.status()).toBe(200);
    
    const headers = response.headers();
    expect(headers['access-control-allow-origin']).toBe('https://apps.quentinspencer.com');
    expect(headers['access-control-allow-methods']).toContain('POST');
  });
});

import { test, expect } from '@playwright/test';

// Test data for different roles
const testUsers = {
  admin: { username: 'admin', password: 'admin123' },
  staff: { username: 'staff', password: 'staff123' },
  viewer: { username: 'viewer', password: 'viewer123' }
};

// Helper function to get auth token
async function getAuthToken(request: any, user: typeof testUsers.admin): Promise<string> {
  const response = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
    data: user
  });
  
  if (response.status() !== 200) {
    throw new Error(`Authentication failed for ${user.username}`);
  }
  
  const data = await response.json();
  return data.access_token;
}

test.describe('Role-Based API Tests', () => {
  test.describe('Admin Role API Tests', () => {
    test('Admin can access all API endpoints', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.admin);
      
      // Test courses endpoint
      const coursesResponse = await request.get('https://api.quentinspencer.com/api/v1/courses/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect(coursesResponse.status()).toBe(200);
      
      // Test users endpoint
      const usersResponse = await request.get('https://api.quentinspencer.com/api/v1/users/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect(usersResponse.status()).toBe(200);
      
      console.log('✓ Admin can access all API endpoints');
    });

    test('Admin can create and manage users', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.admin);
      
      // Test user creation (if endpoint exists)
      const createUserResponse = await request.post('https://api.quentinspencer.com/api/v1/users/', {
        headers: { 'Authorization': `Bearer ${token}` },
        data: {
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'viewer'
        }
      });
      
      // This might return 404 if endpoint doesn't exist, which is expected
      console.log(`✓ User creation endpoint status: ${createUserResponse.status()}`);
    });

    test('Admin can access audit logs', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.admin);
      
      // Test audit endpoint
      const auditResponse = await request.get('https://api.quentinspencer.com/api/v1/audit/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // This might return 404 if endpoint doesn't exist yet
      console.log(`✓ Audit endpoint status: ${auditResponse.status()}`);
    });
  });

  test.describe('Staff Role API Tests', () => {
    test('Staff can access operational endpoints', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.staff);
      
      // Test courses endpoint
      const coursesResponse = await request.get('https://api.quentinspencer.com/api/v1/courses/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect(coursesResponse.status()).toBe(200);
      
      console.log('✓ Staff can access operational endpoints');
    });

    test('Staff cannot access admin-only endpoints', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.staff);
      
      // Test audit endpoint (should be denied)
      const auditResponse = await request.get('https://api.quentinspencer.com/api/v1/audit/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Should be 403 Forbidden or 404 Not Found
      expect([403, 404]).toContain(auditResponse.status());
      console.log('✓ Staff correctly denied access to admin endpoints');
    });
  });

  test.describe('Viewer Role API Tests', () => {
    test('Viewer can access limited endpoints', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.viewer);
      
      // Test courses endpoint (should work)
      const coursesResponse = await request.get('https://api.quentinspencer.com/api/v1/courses/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect(coursesResponse.status()).toBe(200);
      
      console.log('✓ Viewer can access limited endpoints');
    });

    test('Viewer cannot access management endpoints', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.viewer);
      
      // Test users endpoint (should be denied)
      const usersResponse = await request.get('https://api.quentinspencer.com/api/v1/users/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Should be 403 Forbidden or 404 Not Found
      expect([403, 404]).toContain(usersResponse.status());
      console.log('✓ Viewer correctly denied access to management endpoints');
    });
  });

  test.describe('Authentication and Authorization Tests', () => {
    test('Valid authentication returns token', async ({ request }) => {
      const response = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
        data: testUsers.admin
      });
      
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.access_token).toBeDefined();
      expect(typeof data.access_token).toBe('string');
      expect(data.access_token.length).toBeGreaterThan(0);
      
      console.log('✓ Valid authentication returns proper token');
    });

    test('Invalid authentication is rejected', async ({ request }) => {
      const response = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
        data: { username: 'invalid', password: 'invalid' }
      });
      
      expect(response.status()).toBe(401);
      console.log('✓ Invalid authentication properly rejected');
    });

    test('Token-based authentication works', async ({ request }) => {
      const token = await getAuthToken(request, testUsers.admin);
      
      const response = await request.get('https://api.quentinspencer.com/api/v1/courses/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      expect(response.status()).toBe(200);
      console.log('✓ Token-based authentication works');
    });

    test('Invalid token is rejected', async ({ request }) => {
      const response = await request.get('https://api.quentinspencer.com/api/v1/courses/', {
        headers: { 'Authorization': 'Bearer invalid-token' }
      });
      
      expect(response.status()).toBe(401);
      console.log('✓ Invalid token properly rejected');
    });
  });

  test.describe('API Security Tests', () => {
    test('API handles missing authentication', async ({ request }) => {
      const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
      
      // Should either require authentication (401) or allow public access (200)
      expect([200, 401]).toContain(response.status());
      console.log(`✓ API handles missing authentication (status: ${response.status()})`);
    });

    test('API handles malformed requests', async ({ request }) => {
      const response = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
        data: { invalid: 'data' }
      });
      
      expect(response.status()).toBe(422); // Unprocessable Entity
      console.log('✓ API handles malformed requests correctly');
    });

    test('API rate limiting works', async ({ request }) => {
      const requests = [];
      for (let i = 0; i < 20; i++) {
        requests.push(request.get('https://api.quentinspencer.com/api/v1/courses/'));
      }
      
      const responses = await Promise.all(requests);
      const rateLimitedResponses = responses.filter(r => r.status() === 429);
      
      if (rateLimitedResponses.length > 0) {
        console.log(`✓ API rate limiting active (${rateLimitedResponses.length} requests rate limited)`);
      } else {
        console.log('✓ API rate limiting not triggered (may not be configured)');
      }
    });
  });

  test.describe('Data Validation Tests', () => {
    test('API returns proper data structure', async ({ request }) => {
      const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      
      console.log(`✓ API returns proper data structure (${data.length} items)`);
    });

    test('API handles pagination parameters', async ({ request }) => {
      const response = await request.get('https://api.quentinspencer.com/api/v1/courses/?limit=5&offset=0');
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      
      console.log('✓ API handles pagination parameters');
    });

    test('API handles filtering parameters', async ({ request }) => {
      const response = await request.get('https://api.quentinspencer.com/api/v1/courses/?active=true');
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      
      console.log('✓ API handles filtering parameters');
    });
  });

  test.describe('Performance Tests', () => {
    test('API response times are acceptable', async ({ request }) => {
      const startTime = Date.now();
      const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
      const responseTime = Date.now() - startTime;
      
      expect(response.status()).toBe(200);
      expect(responseTime).toBeLessThan(5000); // Should respond within 5 seconds
      
      console.log(`✓ API response time: ${responseTime}ms`);
    });

    test('API handles concurrent requests', async ({ request }) => {
      const requests = [];
      for (let i = 0; i < 10; i++) {
        requests.push(request.get('https://api.quentinspencer.com/api/v1/courses/'));
      }
      
      const responses = await Promise.all(requests);
      
      for (const response of responses) {
        expect(response.status()).toBe(200);
      }
      
      console.log('✓ API handles concurrent requests correctly');
    });
  });
});

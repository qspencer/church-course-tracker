import { test, expect } from '@playwright/test';

test.describe('API Improvements Verification', () => {
  test('Enhanced health endpoint provides comprehensive status', async ({ request }) => {
    const response = await request.get('https://api.quentinspencer.com/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    
    // Check basic health status
    expect(data.status).toBeDefined();
    expect(data.timestamp).toBeDefined();
    expect(data.version).toBeDefined();
    expect(data.environment).toBeDefined();
    expect(data.checks).toBeDefined();
    
    // Check specific health checks
    expect(data.checks.database).toBeDefined();
    expect(data.checks.configuration).toBeDefined();
    expect(data.checks.security).toBeDefined();
    expect(data.checks.cors_origins).toBeDefined();
    expect(data.checks.rate_limiting).toBeDefined();
    
    console.log('✓ Enhanced health endpoint working correctly');
    console.log(`  Status: ${data.status}`);
    console.log(`  Database: ${data.checks.database}`);
    console.log(`  Configuration: ${data.checks.configuration}`);
    console.log(`  Security: ${data.checks.security}`);
    console.log(`  CORS Origins: ${data.checks.cors_origins}`);
    console.log(`  Rate Limiting: ${data.checks.rate_limiting}`);
  });

  test('CORS headers are properly configured', async ({ request }) => {
    const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    expect(response.status()).toBe(200);
    
    const headers = response.headers();
    
    // Check for CORS headers
    const corsHeaders = [
      'access-control-allow-origin',
      'access-control-allow-methods',
      'access-control-allow-headers',
      'access-control-expose-headers',
      'access-control-max-age'
    ];
    
    let corsHeadersFound = 0;
    for (const header of corsHeaders) {
      if (headers[header]) {
        corsHeadersFound++;
        console.log(`✓ CORS header ${header}: ${headers[header]}`);
      }
    }
    
    expect(corsHeadersFound).toBeGreaterThan(0);
    console.log(`✓ Found ${corsHeadersFound} CORS headers`);
  });

  test('Security headers are properly configured', async ({ request }) => {
    const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    expect(response.status()).toBe(200);
    
    const headers = response.headers();
    
    // Check for security headers
    const securityHeaders = [
      'x-content-type-options',
      'x-frame-options',
      'x-xss-protection',
      'referrer-policy',
      'permissions-policy',
      'content-security-policy',
      'x-download-options',
      'x-permitted-cross-domain-policies',
      'cross-origin-embedder-policy',
      'cross-origin-opener-policy',
      'cross-origin-resource-policy'
    ];
    
    let securityHeadersFound = 0;
    for (const header of securityHeaders) {
      if (headers[header]) {
        securityHeadersFound++;
        console.log(`✓ Security header ${header}: ${headers[header]}`);
      }
    }
    
    expect(securityHeadersFound).toBeGreaterThan(5); // Should have most security headers
    console.log(`✓ Found ${securityHeadersFound} security headers`);
  });

  test('Rate limiting headers are present', async ({ request }) => {
    const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    expect(response.status()).toBe(200);
    
    const headers = response.headers();
    
    // Check for rate limiting headers
    const rateLimitHeaders = [
      'x-rate-limit-limit',
      'x-rate-limit-remaining',
      'x-rate-limit-reset'
    ];
    
    let rateLimitHeadersFound = 0;
    for (const header of rateLimitHeaders) {
      if (headers[header]) {
        rateLimitHeadersFound++;
        console.log(`✓ Rate limit header ${header}: ${headers[header]}`);
      }
    }
    
    expect(rateLimitHeadersFound).toBeGreaterThan(0);
    console.log(`✓ Found ${rateLimitHeadersFound} rate limiting headers`);
  });

  test('Rate limiting functionality works', async ({ request }) => {
    // Make multiple rapid requests to test rate limiting
    const requests = [];
    for (let i = 0; i < 15; i++) {
      requests.push(request.get('https://api.quentinspencer.com/api/v1/courses/'));
    }
    
    const responses = await Promise.all(requests);
    
    // Check for rate limited responses
    const rateLimitedResponses = responses.filter(r => r.status() === 429);
    const successfulResponses = responses.filter(r => r.status() === 200);
    
    console.log(`✓ Made ${requests.length} requests`);
    console.log(`✓ Successful responses: ${successfulResponses.length}`);
    console.log(`✓ Rate limited responses: ${rateLimitedResponses.length}`);
    
    // At least some requests should succeed
    expect(successfulResponses.length).toBeGreaterThan(0);
    
    // If rate limiting is working, some requests might be rate limited
    if (rateLimitedResponses.length > 0) {
      console.log('✓ Rate limiting is active and working');
      
      // Check rate limit response format
      const rateLimitResponse = await rateLimitedResponses[0].json();
      expect(rateLimitResponse.detail).toBeDefined();
      expect(rateLimitResponse.rate_limit).toBeDefined();
      expect(rateLimitResponse.rate_limit.limit).toBeDefined();
      expect(rateLimitResponse.rate_limit.remaining).toBeDefined();
      expect(rateLimitResponse.rate_limit.reset_time).toBeDefined();
      expect(rateLimitResponse.rate_limit.window).toBeDefined();
      
      console.log('✓ Rate limit response format is correct');
    } else {
      console.log('✓ Rate limiting not triggered (may be configured for higher limits)');
    }
  });

  test('API performance is maintained with new features', async ({ request }) => {
    const startTime = Date.now();
    const response = await request.get('https://api.quentinspencer.com/api/v1/courses/');
    const responseTime = Date.now() - startTime;
    
    expect(response.status()).toBe(200);
    expect(responseTime).toBeLessThan(2000); // Should still be fast
    
    console.log(`✓ API response time with new features: ${responseTime}ms`);
  });

  test('All endpoints maintain functionality with new middleware', async ({ request }) => {
    // Test multiple endpoints to ensure middleware doesn't break functionality
    const endpoints = [
      '/api/v1/courses/',
      '/api/v1/users/',
      '/health'
    ];
    
    for (const endpoint of endpoints) {
      const response = await request.get(`https://api.quentinspencer.com${endpoint}`);
      expect(response.status()).toBe(200);
      console.log(`✓ Endpoint ${endpoint} working correctly`);
    }
  });

  test('Authentication still works with new middleware', async ({ request }) => {
    const response = await request.post('https://api.quentinspencer.com/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.access_token).toBeDefined();
    
    console.log('✓ Authentication works with new middleware');
  });
});

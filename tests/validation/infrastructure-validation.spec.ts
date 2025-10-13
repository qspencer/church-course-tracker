import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Infrastructure Validation Tests', () => {
  const infraPath = path.join(process.cwd(), 'infrastructure');

  test('API Gateway configuration file exists and is valid', () => {
    const apiGatewayFile = path.join(infraPath, 'api_gateway.tf');
    expect(fs.existsSync(apiGatewayFile)).toBeTruthy();
    
    const content = fs.readFileSync(apiGatewayFile, 'utf-8');
    
    // Verify key resources exist
    expect(content).toContain('resource "aws_apigatewayv2_api"');
    expect(content).toContain('resource "aws_apigatewayv2_vpc_link"');
    expect(content).toContain('resource "aws_service_discovery_service"');
    expect(content).toContain('resource "aws_apigatewayv2_domain_name"');
    
    // Verify cost-saving measures
    expect(content).not.toContain('aws_lb');  // No ALB
    expect(content).not.toContain('Application Load Balancer');
    
    console.log('✅ API Gateway configuration is valid');
  });

  test('ALB resources have been removed from main.tf', () => {
    const mainFile = path.join(infraPath, 'main.tf');
    expect(fs.existsSync(mainFile)).toBeTruthy();
    
    const content = fs.readFileSync(mainFile, 'utf-8');
    
    // Verify ALB resources are NOT present
    expect(content).not.toContain('resource "aws_lb" "main"');
    expect(content).not.toContain('resource "aws_lb_target_group"');
    expect(content).not.toContain('resource "aws_lb_listener"');
    
    // Verify API Gateway is referenced
    expect(content).toContain('api_gateway.tf');
    
    console.log('✅ ALB resources successfully removed');
  });

  test('ECS service updated with service discovery', () => {
    const ecsFile = path.join(infraPath, 'ecs.tf');
    expect(fs.existsSync(ecsFile)).toBeTruthy();
    
    const content = fs.readFileSync(ecsFile, 'utf-8');
    
    // Verify service discovery is configured
    expect(content).toContain('service_registries');
    expect(content).toContain('aws_service_discovery_service');
    
    // Verify load_balancer block is removed
    expect(content).not.toContain('load_balancer {');
    expect(content).not.toContain('target_group_arn');
    
    console.log('✅ ECS service discovery configured correctly');
  });

  test('CloudWatch monitoring updated for API Gateway', () => {
    const cloudwatchFile = path.join(infraPath, 'cloudwatch.tf');
    expect(fs.existsSync(cloudwatchFile)).toBeTruthy();
    
    const content = fs.readFileSync(cloudwatchFile, 'utf-8');
    
    // Verify API Gateway metrics exist
    expect(content).toContain('AWS/ApiGateway');
    expect(content).toContain('Count');
    expect(content).toContain('4XXError');
    expect(content).toContain('5XXError');
    expect(content).toContain('Latency');
    
    // Verify ALB metrics removed
    expect(content).not.toContain('AWS/ApplicationELB');
    
    console.log('✅ CloudWatch monitoring updated correctly');
  });

  test('Security groups updated for VPC Link', () => {
    const mainFile = path.join(infraPath, 'main.tf');
    const content = fs.readFileSync(mainFile, 'utf-8');
    
    // Verify ECS security group allows traffic from API Gateway VPC Link
    expect(content).toContain('aws_security_group.api_gateway_vpc_link');
    
    // Verify ALB security group is removed
    expect(content).not.toContain('resource "aws_security_group" "alb"');
    
    console.log('✅ Security groups configured correctly');
  });

  test('Route 53 points to API Gateway instead of ALB', () => {
    const mainFile = path.join(infraPath, 'main.tf');
    const content = fs.readFileSync(mainFile, 'utf-8');
    
    // Verify Route 53 record for API points to API Gateway
    expect(content).toContain('aws_apigatewayv2_domain_name.main');
    expect(content).toContain('target_domain_name');
    
    // Verify it doesn't point to ALB
    expect(content).not.toContain('aws_lb.main.dns_name');
    
    console.log('✅ Route 53 configured for API Gateway');
  });

  test('Outputs updated with API Gateway information', () => {
    const outputsFile = path.join(infraPath, 'outputs.tf');
    expect(fs.existsSync(outputsFile)).toBeTruthy();
    
    const content = fs.readFileSync(outputsFile, 'utf-8');
    
    // Verify API Gateway outputs exist
    expect(content).toContain('api_gateway_endpoint');
    expect(content).toContain('api_gateway_domain');
    expect(content).toContain('aws_apigatewayv2_api');
    
    // Verify ALB outputs removed
    expect(content).not.toContain('alb_dns_name');
    
    console.log('✅ Outputs updated correctly');
  });
});

test.describe('CI/CD Pipeline Validation Tests', () => {
  const workflowPath = path.join(process.cwd(), '.github', 'workflows');

  test('Backend tests workflow exists and is valid', () => {
    const workflowFile = path.join(workflowPath, 'backend-tests.yml');
    expect(fs.existsSync(workflowFile)).toBeTruthy();
    
    const content = fs.readFileSync(workflowFile, 'utf-8');
    
    // Verify key components
    expect(content).toContain('name: Backend Tests');
    expect(content).toContain('pytest');
    expect(content).toContain('--cov=app');
    expect(content).toContain('python-version: \'3.11\'');
    
    console.log('✅ Backend tests workflow is valid');
  });

  test('Frontend tests workflow exists and is valid', () => {
    const workflowFile = path.join(workflowPath, 'frontend-tests.yml');
    expect(fs.existsSync(workflowFile)).toBeTruthy();
    
    const content = fs.readFileSync(workflowFile, 'utf-8');
    
    // Verify key components
    expect(content).toContain('name: Frontend Tests');
    expect(content).toContain('npm ci');
    expect(content).toContain('npm run test:headless');
    expect(content).toContain('node-version: \'18\'');
    
    console.log('✅ Frontend tests workflow is valid');
  });

  test('E2E tests workflow exists and is valid', () => {
    const workflowFile = path.join(workflowPath, 'e2e-tests.yml');
    expect(fs.existsSync(workflowFile)).toBeTruthy();
    
    const content = fs.readFileSync(workflowFile, 'utf-8');
    
    // Verify key components
    expect(content).toContain('name: E2E Tests');
    expect(content).toContain('playwright');
    expect(content).toContain('npm test');
    expect(content).toContain('schedule');  // Daily schedule
    
    console.log('✅ E2E tests workflow is valid');
  });

  test('Deployment workflow exists and is valid', () => {
    const workflowFile = path.join(workflowPath, 'deploy.yml');
    expect(fs.existsSync(workflowFile)).toBeTruthy();
    
    const content = fs.readFileSync(workflowFile, 'utf-8');
    
    // Verify key components
    expect(content).toContain('name: Deploy to AWS');
    expect(content).toContain('deploy-backend');
    expect(content).toContain('deploy-frontend');
    expect(content).toContain('ECR');
    expect(content).toContain('ECS');
    expect(content).toContain('S3');
    expect(content).toContain('CloudFront');
    
    console.log('✅ Deployment workflow is valid');
  });

  test('All workflows have proper trigger configuration', () => {
    const workflows = [
      'backend-tests.yml',
      'frontend-tests.yml',
      'e2e-tests.yml',
      'deploy.yml'
    ];
    
    workflows.forEach(workflow => {
      const workflowFile = path.join(workflowPath, workflow);
      const content = fs.readFileSync(workflowFile, 'utf-8');
      
      // Verify triggers exist
      expect(content).toContain('on:');
      expect(content).toMatch(/push:|pull_request:|schedule:|workflow_dispatch:/);
    });
    
    console.log('✅ All workflows have proper triggers');
  });
});

test.describe('Documentation Validation Tests', () => {
  const docsPath = path.join(process.cwd(), 'docs');

  test('CI/CD setup documentation exists', () => {
    const docFile = path.join(docsPath, 'CI_CD_SETUP.md');
    expect(fs.existsSync(docFile)).toBeTruthy();
    
    const content = fs.readFileSync(docFile, 'utf-8');
    expect(content.length).toBeGreaterThan(1000);  // Substantial content
    expect(content).toContain('GitHub Actions');
    expect(content).toContain('Secrets');
    
    console.log('✅ CI/CD documentation exists');
  });

  test('Architecture update documentation exists', () => {
    const docFile = path.join(docsPath, 'ARCHITECTURE_UPDATE.md');
    expect(fs.existsSync(docFile)).toBeTruthy();
    
    const content = fs.readFileSync(docFile, 'utf-8');
    expect(content).toContain('ALB');
    expect(content).toContain('API Gateway');
    expect(content).toContain('Cost');
    expect(content).toContain('savings');
    
    console.log('✅ Architecture documentation exists');
  });

  test('Summary documentation exists', () => {
    const summaryFiles = [
      'INFRASTRUCTURE_UPDATE_SUMMARY.md',
      'CHANGES_SUMMARY.md',
      'TEST_VALIDATION_REPORT.md'
    ];
    
    summaryFiles.forEach(file => {
      const filePath = path.join(process.cwd(), file);
      expect(fs.existsSync(filePath)).toBeTruthy();
    });
    
    console.log('✅ All summary documentation exists');
  });
});

test.describe('Configuration Validation Tests', () => {
  test('README updated with new architecture', () => {
    const readmeFile = path.join(process.cwd(), 'README.md');
    expect(fs.existsSync(readmeFile)).toBeTruthy();
    
    const content = fs.readFileSync(readmeFile, 'utf-8');
    
    // Verify updates
    expect(content).toContain('API Gateway');
    expect(content).toContain('Service Discovery');
    expect(content).toContain('CI/CD');
    
    console.log('✅ README updated correctly');
  });

  test('Playwright configuration is valid', () => {
    const configFile = path.join(process.cwd(), 'playwright.config.ts');
    expect(fs.existsSync(configFile)).toBeTruthy();
    
    const content = fs.readFileSync(configFile, 'utf-8');
    expect(content).toContain('testDir');
    expect(content).toContain('use:');
    
    console.log('✅ Playwright configuration is valid');
  });

  test('Package.json has Playwright dependency', () => {
    const packageFile = path.join(process.cwd(), 'package.json');
    expect(fs.existsSync(packageFile)).toBeTruthy();
    
    const content = JSON.parse(fs.readFileSync(packageFile, 'utf-8'));
    expect(content.devDependencies['@playwright/test']).toBeDefined();
    
    console.log('✅ Playwright dependency configured');
  });
});


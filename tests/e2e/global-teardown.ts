/**
 * Playwright Global Teardown
 * 
 * This file runs once after all tests complete.
 * It removes CSV-loaded test data from the database to clean up after tests.
 */

import { execSync } from 'child_process';
import { resolve } from 'path';

async function globalTeardown() {
  console.log('🧹 Cleaning up test data...');
  
  // Check if we should skip data cleanup (e.g., when testing against production)
  if (process.env.E2E_SKIP_DATA_CLEANUP === 'true') {
    console.log('⏭️  Skipping test data cleanup (E2E_SKIP_DATA_CLEANUP=true)');
    return;
  }
  
  try {
    // Get the directory where this file is located
    const scriptDir = __dirname;
    const teardownScript = resolve(scriptDir, 'teardown-test-data.py');
    
    // Run the Python script to clear test data
    // Change to project root to ensure backend dependencies are available
    const projectRoot = resolve(scriptDir, '../..');
    console.log(`Running: python3 ${teardownScript}`);
    const output = execSync(`python3 "${teardownScript}"`, {
      encoding: 'utf-8',
      stdio: 'inherit',
      cwd: projectRoot,
      env: { ...process.env, PYTHONPATH: resolve(projectRoot, 'backend') },
    });
    
    console.log('✅ Test data cleaned up successfully!');
    return;
  } catch (error: any) {
    const errorMessage = error?.message || String(error);
    console.error('❌ Failed to clean up test data:', errorMessage);
    
    // Check if it's a Python/module import error (expected in CI without Python deps)
    if (errorMessage.includes('ModuleNotFoundError') || 
        errorMessage.includes('No module named') ||
        errorMessage.includes('python3: command not found')) {
      console.warn('⚠️  Python dependencies not available - this is expected in CI');
      console.warn('   Set E2E_SKIP_DATA_CLEANUP=true to suppress this warning');
    } else {
      console.warn('⚠️  Test data cleanup failed - manual cleanup may be required');
      console.warn('   Set E2E_SKIP_DATA_CLEANUP=true to suppress this warning');
    }
    
    // Log error but don't fail - data cleanup is best effort
    return;
  }
}

export default globalTeardown;


/**
 * Playwright Global Setup
 * 
 * This file runs once before all tests start.
 * It loads CSV test data into the database to ensure tests have the data they need.
 */

import { execSync } from 'child_process';
import { resolve } from 'path';

async function globalSetup() {
  console.log('🔧 Setting up test data...');
  
  // Check if we should skip data loading (e.g., when testing against production)
  if (process.env.E2E_SKIP_DATA_LOAD === 'true') {
    console.log('⏭️  Skipping test data load (E2E_SKIP_DATA_LOAD=true)');
    console.log('   Tests will use existing data in the database');
    return;
  }
  
  try {
    // Get the directory where this file is located
    const scriptDir = __dirname;
    const setupScript = resolve(scriptDir, 'setup-test-data.py');
    
    // Run the Python script to load test data
    // Change to project root to ensure backend dependencies are available
    const projectRoot = resolve(scriptDir, '../..');
    console.log(`Running: python3 ${setupScript}`);
    const output = execSync(`python3 "${setupScript}" --force`, {
      encoding: 'utf-8',
      stdio: 'inherit',
      cwd: projectRoot,
      env: { ...process.env, PYTHONPATH: resolve(projectRoot, 'backend') },
    });
    
    console.log('✅ Test data loaded successfully!');
    return;
  } catch (error) {
    console.error('❌ Failed to load test data:', error);
    // Don't fail the test run if data loading fails - tests might still work
    // with existing data or skip gracefully
    console.warn('⚠️  Continuing with test run - some tests may skip if data is missing');
    console.warn('   Set E2E_SKIP_DATA_LOAD=true to suppress this warning');
    return;
  }
}

export default globalSetup;


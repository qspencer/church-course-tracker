/**
 * Playwright Global Setup
 *
 * This file runs once before all tests start.
 * It loads environment variables from .env.e2e and sets up test data.
 */

import { execSync } from 'child_process';
import { resolve, join } from 'path';
import { existsSync, readFileSync } from 'fs';

/**
 * Load environment variables from a .env file
 */
function loadEnvFile(filePath: string): void {
  if (!existsSync(filePath)) {
    return;
  }

  console.log(`📁 Loading environment from: ${filePath}`);
  const content = readFileSync(filePath, 'utf-8');

  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    // Skip comments and empty lines
    if (!trimmed || trimmed.startsWith('#')) continue;

    const match = trimmed.match(/^([^=]+)=(.*)$/);
    if (match) {
      const key = match[1].trim();
      let value = match[2].trim();
      // Remove quotes if present
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      // Only set if not already set (allow CLI overrides)
      if (!process.env[key]) {
        process.env[key] = value;
      }
    }
  }
}

async function globalSetup() {
  const scriptDir = __dirname;
  const projectRoot = resolve(scriptDir, '../..');

  // Load .env.e2e file if it exists
  const envFile = join(scriptDir, '.env.e2e');
  loadEnvFile(envFile);

  // Also try loading from project root
  const rootEnvFile = join(projectRoot, '.env.e2e');
  if (rootEnvFile !== envFile) {
    loadEnvFile(rootEnvFile);
  }

  console.log('🔧 Setting up test data...');

  // Log target environment
  const appUrl = process.env.APP_BASE_URL || process.env.PLAYWRIGHT_BASE_URL || 'not set';
  const apiUrl = process.env.API_BASE_URL || 'not set';
  console.log(`   Target app: ${appUrl}`);
  console.log(`   Target API: ${apiUrl}`);

  // Check if credentials are configured
  const hasAdmin = !!(process.env.E2E_ADMIN_USERNAME && process.env.E2E_ADMIN_PASSWORD);
  const hasStaff = !!(process.env.E2E_STAFF_USERNAME && process.env.E2E_STAFF_PASSWORD);
  const hasViewer = !!(process.env.E2E_VIEWER_USERNAME && process.env.E2E_VIEWER_PASSWORD);

  console.log(`   Credentials: admin=${hasAdmin ? '✓' : '✗'} staff=${hasStaff ? '✓' : '✗'} viewer=${hasViewer ? '✓' : '✗'}`);

  if (!hasAdmin && !hasStaff && !hasViewer) {
    console.warn('⚠️  No test credentials configured');
    console.warn('   Run: ./tests/e2e/scripts/setup-local-e2e.sh');
    console.warn('   Or create tests/e2e/.env.e2e with credentials');
  }

  // Check if we should skip data loading (e.g., when testing against production)
  if (process.env.E2E_SKIP_DATA_LOAD === 'true') {
    console.log('⏭️  Skipping test data load (E2E_SKIP_DATA_LOAD=true)');
    console.log('   Tests will use existing data in the database');
    return;
  }

  try {
    const setupScript = resolve(scriptDir, 'setup-test-data.py');

    // Try to use the backend's virtual environment if available
    const venvPython = resolve(projectRoot, 'backend/venv/bin/python3');
    const pythonCmd = existsSync(venvPython) ? venvPython : 'python3';

    console.log(`Running: ${pythonCmd} ${setupScript}`);
    execSync(`"${pythonCmd}" "${setupScript}" --force`, {
      encoding: 'utf-8',
      stdio: 'inherit',
      cwd: projectRoot,
      env: { ...process.env, PYTHONPATH: resolve(projectRoot, 'backend') },
    });

    console.log('✅ Test data loaded successfully!');
    return;
  } catch (error: any) {
    const errorMessage = error?.message || String(error);
    console.error('❌ Failed to load test data:', errorMessage);

    // Check if it's a Python/module import error (expected in CI without Python deps)
    if (errorMessage.includes('ModuleNotFoundError') ||
        errorMessage.includes('No module named') ||
        errorMessage.includes('python3: command not found')) {
      console.warn('⚠️  Python dependencies not available - this is expected in CI');
      console.warn('   Set E2E_SKIP_DATA_LOAD=true to suppress this warning');
    } else {
      console.warn('⚠️  Continuing with test run - some tests may skip if data is missing');
      console.warn('   Set E2E_SKIP_DATA_LOAD=true to suppress this warning');
    }

    // Don't fail the test run if data loading fails - tests might still work
    // with existing data or skip gracefully
    return;
  }
}

export default globalSetup;

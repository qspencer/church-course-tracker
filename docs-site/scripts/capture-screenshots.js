"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const test_1 = require("@playwright/test");
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const BASE_URL = 'https://apps.quentinspencer.com/churchcoursetracker';
const SCREENSHOT_DIR = path.join(__dirname, '../docs/images/screenshots');
// Create directories if they don't exist
const dirs = [
    path.join(SCREENSHOT_DIR, 'getting-started'),
    path.join(SCREENSHOT_DIR, 'user-guide'),
];
dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});
const screenshots = [
    // Getting Started screenshots
    {
        name: 'login-page.png',
        url: `${BASE_URL}/auth`,
        directory: 'getting-started',
        waitFor: 'input[formControlName="username"]',
        fullPage: true,
        delay: 2000,
    },
    {
        name: 'login-form.png',
        url: `${BASE_URL}/auth`,
        directory: 'getting-started',
        waitFor: 'input[formControlName="username"]',
        fullPage: false,
        delay: 2000,
    },
    // Note: Dashboard and other authenticated pages require login
    // These will be captured if credentials are provided
];
async function takeScreenshot(page, config) {
    try {
        console.log(`📸 Capturing: ${config.name}...`);
        await page.goto(config.url, { waitUntil: 'networkidle' });
        if (config.waitFor) {
            await page.waitForSelector(config.waitFor, { timeout: 10000 });
        }
        if (config.delay) {
            await page.waitForTimeout(config.delay);
        }
        const filePath = path.join(SCREENSHOT_DIR, config.directory, config.name);
        await page.screenshot({
            path: filePath,
            fullPage: config.fullPage ?? true,
        });
        console.log(`✅ Saved: ${filePath}`);
    }
    catch (error) {
        console.error(`❌ Failed to capture ${config.name}:`, error);
    }
}
async function captureAuthenticatedScreenshots(page, username, password) {
    try {
        console.log('🔐 Logging in...');
        // Navigate to login page
        await page.goto(`${BASE_URL}/auth`, { waitUntil: 'networkidle' });
        await page.waitForSelector('input[formControlName="username"]', { timeout: 10000 });
        // Fill in credentials
        await page.fill('input[formControlName="username"]', username);
        await page.fill('input[formControlName="password"]', password);
        // Click login button
        await page.click('button[type="submit"]');
        // Wait for navigation after login
        await page.waitForURL('**/dashboard**', { timeout: 15000 }).catch(() => {
            // If URL doesn't change, wait for dashboard elements
            return page.waitForSelector('mat-sidenav, .dashboard, [class*="dashboard"]', { timeout: 15000 });
        });
        await page.waitForTimeout(3000);
        // Dashboard screenshot
        console.log('📸 Capturing dashboard...');
        await page.screenshot({
            path: path.join(SCREENSHOT_DIR, 'getting-started', 'dashboard.png'),
            fullPage: true,
        });
        console.log('✅ Saved: dashboard.png');
        // Navigation menu screenshot
        console.log('📸 Capturing navigation menu...');
        await page.screenshot({
            path: path.join(SCREENSHOT_DIR, 'getting-started', 'navigation-menu.png'),
            fullPage: false,
        });
        console.log('✅ Saved: navigation-menu.png');
        // Try to navigate to courses page
        try {
            await page.goto(`${BASE_URL}/courses`, { waitUntil: 'networkidle' });
            await page.waitForTimeout(2000);
            await page.screenshot({
                path: path.join(SCREENSHOT_DIR, 'user-guide', 'courses-list.png'),
                fullPage: true,
            });
            console.log('✅ Saved: courses-list.png');
        }
        catch (error) {
            console.log('⚠️  Could not capture courses list');
        }
        // Try to find and capture create course form
        try {
            const createButton = page.locator('button:has-text("Create"), button:has-text("New"), [class*="create"], [class*="add"]').first();
            if (await createButton.count() > 0) {
                await createButton.click();
                await page.waitForTimeout(2000);
                await page.screenshot({
                    path: path.join(SCREENSHOT_DIR, 'user-guide', 'create-course-form.png'),
                    fullPage: true,
                });
                console.log('✅ Saved: create-course-form.png');
                // Close the form
                await page.keyboard.press('Escape');
            }
        }
        catch (error) {
            console.log('⚠️  Could not capture create course form');
        }
        // Try to capture progress page
        try {
            await page.goto(`${BASE_URL}/progress`, { waitUntil: 'networkidle' });
            await page.waitForTimeout(2000);
            await page.screenshot({
                path: path.join(SCREENSHOT_DIR, 'user-guide', 'progress-tracking.png'),
                fullPage: true,
            });
            console.log('✅ Saved: progress-tracking.png');
        }
        catch (error) {
            console.log('⚠️  Could not capture progress page');
        }
    }
    catch (error) {
        console.error('❌ Failed to capture authenticated screenshots:', error);
    }
}
async function main() {
    const browser = await test_1.chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
    });
    const page = await context.newPage();
    console.log('🚀 Starting screenshot capture...\n');
    // Capture public screenshots
    for (const config of screenshots) {
        await takeScreenshot(page, config);
    }
    // Check if credentials are provided
    const username = process.env.DOCS_USERNAME;
    const password = process.env.DOCS_PASSWORD;
    if (username && password) {
        console.log('\n🔐 Credentials provided, capturing authenticated pages...\n');
        await captureAuthenticatedScreenshots(page, username, password);
    }
    else {
        console.log('\n⚠️  No credentials provided (DOCS_USERNAME, DOCS_PASSWORD)');
        console.log('   Skipping authenticated screenshots (dashboard, navigation, etc.)');
        console.log('   To capture these, set environment variables:');
        console.log('   export DOCS_USERNAME="your-username"');
        console.log('   export DOCS_PASSWORD="your-password"');
    }
    await browser.close();
    console.log('\n✨ Screenshot capture complete!');
}
main().catch(console.error);

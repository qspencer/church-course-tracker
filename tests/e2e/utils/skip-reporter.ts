import { mkdirSync, writeFileSync } from 'fs';
import path from 'path';
import type { Reporter, TestCase, TestResult } from '@playwright/test/reporter';

interface SkippedTestSummary {
  titlePath: string[];
  projectName?: string;
  location?: string;
  repeatEachIndex: number;
  workerIndex: number;
  reason?: string;
}

class SkippedTestsReporter implements Reporter {
  private skipped: SkippedTestSummary[] = [];

  onTestEnd(test: TestCase, result: TestResult): void {
    if (result.status !== 'skipped') {
      return;
    }

    // Try multiple sources for skip reason
    // When testInfo.skip() is called, it sets an annotation with type 'skip'
    // The description contains the skip message
    const skipAnnotation = test.annotations.find((annotation) => annotation.type === 'skip');
    const skipDescription = skipAnnotation?.description;
    
    // Also check for error message (sometimes skip reasons are in errors)
    const errorMessage = result.error?.message?.trim();
    
    // Check if error message contains skip-related text
    const skipFromError = errorMessage && (
      errorMessage.includes('skip') || 
      errorMessage.includes('Skip') ||
      errorMessage.includes('not available') ||
      errorMessage.includes('not configured') ||
      errorMessage.includes('failed to authenticate')
    ) ? errorMessage : undefined;
    
    // Priority: skip annotation description > error message (if skip-related) > error message > default
    const reason =
      skipDescription ||
      skipFromError ||
      errorMessage ||
      (result.error ? String(result.error) : undefined) ||
      'Test was skipped (no reason provided)';

    const location = test.location
      ? `${path.relative(process.cwd(), test.location.file)}:${test.location.line}:${test.location.column}`
      : undefined;

    const projectName = test.parent.project()?.name;

    this.skipped.push({
      titlePath: test.titlePath(),
      projectName,
      location,
      repeatEachIndex: result.repeatEachIndex,
      workerIndex: result.workerIndex,
      reason,
    });
  }

  onEnd(): void {
    const outputDir = path.resolve(process.cwd(), 'test-results');
    mkdirSync(outputDir, { recursive: true });

    const report = {
      generatedAt: new Date().toISOString(),
      totalSkipped: this.skipped.length,
      tests: this.skipped,
    };

    const outputPath = path.join(outputDir, 'skipped-tests.json');
    writeFileSync(outputPath, JSON.stringify(report, null, 2), 'utf-8');

    if (this.skipped.length > 0) {
      console.log(`\nSkipped tests summary written to ${outputPath}`);
    }
  }
}

export default SkippedTestsReporter;


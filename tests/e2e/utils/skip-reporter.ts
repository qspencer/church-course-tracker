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

    const reason =
      result.error?.message?.trim() ||
      test.annotations.find((annotation) => annotation.type === 'skip')?.description ||
      undefined;

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


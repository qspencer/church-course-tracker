#!/usr/bin/env python3
"""
Helper script to run a subset of Playwright tests with:
 1. Explicit subset selection
 2. Wall-clock timing
 3. Automatic cancellation after a configurable timeout
 4. Capturing ALL intermediate output for later analysis

Usage examples:

  # Run a single spec on chromium for up to 900 seconds (15 minutes)
  ./tests/e2e/run_subset_with_timeout.py \
    --timeout-seconds 900 \
    --project chromium \
    tests/e2e/audit-and-security.spec.ts

  # Run a whole directory with default timeout (1800 seconds)
  ./tests/e2e/run_subset_with_timeout.py \
    tests/e2e/user-management.spec.ts
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Run a subset of Playwright tests with a hard wall-clock timeout."
  )
  parser.add_argument(
    "tests",
    nargs="+",
    help="Test files or directories to pass to `npx playwright test` (e.g. tests/e2e/audit-and-security.spec.ts).",
  )
  parser.add_argument(
    "--timeout-seconds",
    type=int,
    default=1800,
    help="Maximum wall-clock time in seconds before the run is cancelled (default: 1800 = 30 minutes).",
  )
  parser.add_argument(
    "--project",
    help="Optional Playwright project name (e.g. chromium). If omitted, uses config defaults.",
  )
  parser.add_argument(
    "--log-file",
    type=str,
    default="test-results/subset-run.log",
    help="Path to write combined stdout/stderr from the test run (default: test-results/subset-run.log).",
  )
  return parser.parse_args()


def ensure_parent_dir(path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)


def build_command(args: argparse.Namespace) -> List[str]:
  cmd: List[str] = ["npx", "playwright", "test"]
  # Put test paths first, then project flag. Some Playwright versions can
  # misinterpret trailing positional args as project names if the order is reversed.
  cmd.extend(args.tests)
  if args.project:
    cmd.extend(["--project", args.project])
  return cmd


def run_with_timeout(args: argparse.Namespace) -> int:
  cmd = build_command(args)
  log_path = Path(args.log_file)
  ensure_parent_dir(log_path)

  start = time.time()

  # Open log file for tee-ing stdout/stderr
  # Use os.open() to ensure file exists and prevent deletion issues
  # We'll keep the file descriptor open and periodically check if file still exists
  log_fd = os.open(
    str(log_path),
    os.O_CREAT | os.O_WRONLY | os.O_TRUNC,
    0o644
  )
  
  log_file = os.fdopen(log_fd, "w", encoding="utf-8", buffering=1)
  
  def reopen_log_file() -> None:
    """Reopen the log file if it was deleted."""
    nonlocal log_file
    try:
      log_file.close()
    except:
      pass
    new_fd = os.open(
      str(log_path),
      os.O_CREAT | os.O_WRONLY | os.O_APPEND,
      0o644
    )
    log_file = os.fdopen(new_fd, "w", encoding="utf-8", buffering=1)
  
  try:
    def log(message: str) -> None:
      """Write a status message to both stdout and the log file."""
      nonlocal log_file
      timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
      line = f"[run_subset_with_timeout {timestamp}] {message}\n"
      sys.stdout.write(line)
      sys.stdout.flush()
      try:
        log_file.write(line)
        log_file.flush()
        # Check if file was deleted and recreate if necessary
        if not log_path.exists():
          reopen_log_file()
          log_file.write(f"[run_subset_with_timeout {timestamp}] Log file was deleted and recreated\n")
          log_file.flush()
      except (OSError, IOError) as e:
        # If write fails, try to recreate the file
        reopen_log_file()
        log_file.write(line)
        log_file.flush()

    # Header status
    log(f"Starting subset run")
    log(f"Command: {' '.join(cmd)}")
    log(f"Log file: {log_path}")
    log(f"Timeout: {args.timeout_seconds} seconds")

    # Start process in a new session so we can kill the whole group on timeout
    proc = subprocess.Popen(
      cmd,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      text=True,
      bufsize=1,
      universal_newlines=True,
      start_new_session=True,
    )

    try:
      # Stream output line-by-line so we always have intermediate logs
      while True:
        line = proc.stdout.readline() if proc.stdout else ""
        if line:
          # Write to both console and log file
          try:
            sys.stdout.write(line)
            sys.stdout.flush()
          except (BrokenPipeError, OSError):
            # stdout might be closed if running in background
            pass
          
          try:
            log_file.write(line)
            log_file.flush()
          except (OSError, IOError):
            # If write fails, try to reopen the file
            reopen_log_file()
            try:
              log_file.write(line)
              log_file.flush()
            except:
              pass

        # Check if process has finished
        if proc.poll() is not None:
          break

        # Check wall-clock timeout
        elapsed = time.time() - start
        if elapsed > args.timeout_seconds:
          log(
            f"Time limit exceeded ({elapsed:.1f}s > {args.timeout_seconds}s). "
            "Cancelling test run..."
          )
          # Kill the whole process group
          try:
            os.killpg(proc.pid, signal.SIGTERM)
          except ProcessLookupError:
            pass

          # Give it a moment to terminate gracefully
          try:
            proc.wait(timeout=10)
          except subprocess.TimeoutExpired:
            try:
              os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
              pass

          # Mark as timeout exit code (distinct from Playwright's codes)
          return 124  # conventionally used by timeout(1)

      elapsed = time.time() - start
      log(f"Completed in {elapsed:.1f} seconds with exit code {proc.returncode}.")
      log(f"Full log: {log_path}")
      return proc.returncode or 0

    finally:
      # Ensure process resources are cleaned up
      if proc and proc.poll() is None:
        try:
          os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
          pass
  finally:
    # Close log file
    try:
      log_file.close()
    except:
      pass


def main() -> int:
  args = parse_args()
  return run_with_timeout(args)


if __name__ == "__main__":
  raise SystemExit(main())



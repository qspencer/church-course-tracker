#!/bin/bash
# Helper script to start Angular frontend
# Note: First run may prompt for autocompletion - answer 'n' manually if needed

cd "$(dirname "$0")/../frontend/church-course-tracker"

# Set environment variables to skip analytics prompts
export NG_CLI_ANALYTICS=false

# Run ng serve directly - if it prompts for autocompletion, it will fail in non-interactive mode
# User should run this once manually to answer the prompt, then it will work
npx ng serve --host 0.0.0.0 --port 4200 --disable-host-check 2>&1

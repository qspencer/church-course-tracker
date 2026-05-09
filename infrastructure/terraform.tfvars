# Production Configuration for apps.eastgate.church
# (changed from "development" 2026-05-09 - this IS the live prod system,
# the original value was misleading and bypassed the production-mode validator
# in app/core/config.py)
aws_region = "us-east-1"
app_name = "church-course-tracker"
environment = "production"
domain_name = "apps.eastgate.church"
certificate_arn = ""  # Will be created automatically

# Cost-optimized settings for development
min_capacity = 1
max_capacity = 3
cpu_target_value = 80
memory_target_value = 85

# CloudWatch alarm notifications (required by infrastructure/cloudwatch.tf)
alert_email = "qspencer@gmail.com"

# Database settings
# WARNING: this value is in cleartext in a tracked file. Phase 4 (DB password
# to Secrets Manager) is the planned fix. Until then, treat this file as
# sensitive and avoid sharing.
db_password = "qicBHo2ypeSkuyrU"

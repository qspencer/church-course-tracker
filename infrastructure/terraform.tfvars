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
# (db_password removed 2026-05-10: the RDS master password is now generated
# by random_password.db in infrastructure/secrets.tf and lives only in
# Terraform state and Secrets Manager. There is no longer a cleartext
# operator value to set here. To manually rotate the password, run:
#   terraform apply -replace=random_password.db
# and then update app_secrets DATABASE_URL via aws secretsmanager
# put-secret-value, and force a new ECS deployment.)

# Secrets Manager Configuration

# Application Secrets
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.app_name}-secrets"
  description             = "Secrets for Church Course Tracker application"
  recovery_window_in_days = 7
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Application Secrets Version
#
# IMPORTANT: the secret_string here is the *bootstrap* value. The live secret
# is updated out-of-band (via `aws secretsmanager put-secret-value`) and now
# contains DATABASE_URL, ADMIN_PASSWORD, USE_MOCK_PLANNING_CENTER, and the
# real Planning Center credentials. Terraform's view (via version_id) is
# stale because secret versions are immutable - terraform reads the version
# it created at first apply, which still exists in version history, so
# `plan` reports no drift even though AWSCURRENT has moved.
#
# The lifecycle.ignore_changes below prevents a future `terraform apply`
# from accidentally creating a new version with the placeholder content
# above and clobbering the live values. Any future change to the secret
# contents must be done via `aws secretsmanager put-secret-value` (or via
# a future, deliberate Terraform-managed JSON encode that mirrors live).
resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    SECRET_KEY                = "your-super-secret-key-change-this-in-production"
    PLANNING_CENTER_APP_ID    = "your-planning-center-app-id"
    PLANNING_CENTER_SECRET    = "your-planning-center-secret"
    PLANNING_CENTER_ACCESS_TOKEN = "your-planning-center-access-token"
  })

  lifecycle {
    ignore_changes = [secret_string, version_stages]
  }
}

# Database Password Secret
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.app_name}-db-password"
  description             = "Database password for Church Course Tracker"
  recovery_window_in_days = 7
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Database Password Secret Version
resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}

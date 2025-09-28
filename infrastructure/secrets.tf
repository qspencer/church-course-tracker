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
resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    SECRET_KEY                = "your-super-secret-key-change-this-in-production"
    PLANNING_CENTER_APP_ID    = "your-planning-center-app-id"
    PLANNING_CENTER_SECRET    = "your-planning-center-secret"
    PLANNING_CENTER_ACCESS_TOKEN = "your-planning-center-access-token"
  })
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

# Lambda function to sync ECS task health to Service Discovery
# This solves the issue where Service Discovery instances remain UNHEALTHY
# even when ECS tasks are HEALTHY, when using custom health check config

resource "aws_lambda_function" "health_sync" {
  filename         = data.archive_file.health_sync_zip.output_path
  function_name    = "${var.app_name}-health-sync"
  role            = aws_iam_role.lambda_health_sync.arn
  handler         = "index.handler"
  source_code_hash = data.archive_file.health_sync_zip.output_base64sha256
  runtime         = "python3.12"
  timeout         = 60

  environment {
    variables = {
      SERVICE_DISCOVERY_SERVICE_ID = aws_service_discovery_service.backend.id
      ECS_CLUSTER                  = aws_ecs_cluster.main.name
      ECS_SERVICE                  = aws_ecs_service.backend.name
    }
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Archive the Lambda function code
data "archive_file" "health_sync_zip" {
  type        = "zip"
  output_path = "${path.module}/health_sync_lambda.zip"
  source {
    content  = file("${path.module}/lambda_health_sync.py")
    filename = "index.py"
  }
}

# Lambda execution role
resource "aws_iam_role" "lambda_health_sync" {
  name = "${var.app_name}-lambda-health-sync-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Lambda policy for Service Discovery
resource "aws_iam_role_policy" "lambda_health_sync" {
  name = "${var.app_name}-lambda-health-sync-policy"
  role = aws_iam_role.lambda_health_sync.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:ListTasks",
          "ecs:DescribeTasks"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "servicediscovery:ListInstances",
          "servicediscovery:GetInstance",
          "servicediscovery:UpdateInstanceCustomHealthStatus"
        ]
        Resource = aws_service_discovery_service.backend.arn
      }
    ]
  })
}

# EventBridge rule to trigger Lambda every 2 minutes
resource "aws_cloudwatch_event_rule" "health_sync_schedule" {
  name                = "${var.app_name}-health-sync-schedule"
  description         = "Trigger health sync Lambda every 2 minutes"
  schedule_expression = "rate(2 minutes)"

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# EventBridge target
resource "aws_cloudwatch_event_target" "health_sync_target" {
  rule      = aws_cloudwatch_event_rule.health_sync_schedule.name
  target_id = "HealthSyncTarget"
  arn       = aws_lambda_function.health_sync.arn
}

# Lambda permission for EventBridge
resource "aws_lambda_permission" "health_sync_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_sync.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.health_sync_schedule.arn
}

# CloudWatch Log Group for Lambda
# Log group is created automatically by Lambda, so we import existing one
# Run: terraform import aws_cloudwatch_log_group.lambda_health_sync /aws/lambda/church-course-tracker-health-sync
resource "aws_cloudwatch_log_group" "lambda_health_sync" {
  name              = "/aws/lambda/${var.app_name}-health-sync"
  retention_in_days = 7

  tags = {
    Environment = var.environment
    Application = var.app_name
  }

  lifecycle {
    ignore_changes = [name]
  }
}


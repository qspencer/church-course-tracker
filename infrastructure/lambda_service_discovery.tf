# Lambda functions for Service Discovery registration/deregistration
# These replace ECS service_registries to avoid ownership conflicts

# Register Lambda - Registers ECS tasks with Service Discovery
resource "aws_lambda_function" "service_discovery_register" {
  filename         = data.archive_file.service_discovery_register_zip.output_path
  function_name    = "${var.app_name}-service-discovery-register"
  role            = aws_iam_role.lambda_service_discovery.arn
  handler         = "index.handler"
  source_code_hash = data.archive_file.service_discovery_register_zip.output_base64sha256
  runtime         = "python3.12"
  timeout         = 60

  environment {
    variables = {
      SERVICE_DISCOVERY_SERVICE_ID = aws_service_discovery_service.backend.id
      SERVICE_DISCOVERY_PORT      = "8000"
    }
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Deregister Lambda - Removes stopped ECS tasks from Service Discovery
resource "aws_lambda_function" "service_discovery_deregister" {
  filename         = data.archive_file.service_discovery_deregister_zip.output_path
  function_name    = "${var.app_name}-service-discovery-deregister"
  role            = aws_iam_role.lambda_service_discovery.arn
  handler         = "index.handler"
  source_code_hash = data.archive_file.service_discovery_deregister_zip.output_base64sha256
  runtime         = "python3.12"
  timeout         = 60

  environment {
    variables = {
      SERVICE_DISCOVERY_SERVICE_ID = aws_service_discovery_service.backend.id
    }
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Archive files for Lambda functions
data "archive_file" "service_discovery_register_zip" {
  type        = "zip"
  output_path = "${path.module}/service_discovery_register_lambda.zip"
  source {
    content  = file("${path.module}/lambda_service_discovery_register.py")
    filename = "index.py"
  }
}

data "archive_file" "service_discovery_deregister_zip" {
  type        = "zip"
  output_path = "${path.module}/service_discovery_deregister_lambda.zip"
  source {
    content  = file("${path.module}/lambda_service_discovery_deregister.py")
    filename = "index.py"
  }
}

# IAM Role for Service Discovery Lambda functions
resource "aws_iam_role" "lambda_service_discovery" {
  name = "${var.app_name}-lambda-service-discovery-role"

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

# IAM Policy for Service Discovery Lambda functions
resource "aws_iam_role_policy" "lambda_service_discovery" {
  name = "${var.app_name}-lambda-service-discovery-policy"
  role = aws_iam_role.lambda_service_discovery.id

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
          "ecs:DescribeTasks",
          "ecs:DescribeTaskDefinition"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeNetworkInterfaces"
        ]
        Resource = "*"
      },
            {
              Effect = "Allow"
              Action = [
                "servicediscovery:RegisterInstance",
                "servicediscovery:DeregisterInstance",
                "servicediscovery:GetInstance",
                "servicediscovery:ListInstances",
                "servicediscovery:GetOperation"
              ]
              Resource = aws_service_discovery_service.backend.arn
            },
            {
              Effect = "Allow"
              Action = [
                "route53:CreateHealthCheck",
                "route53:DeleteHealthCheck",
                "route53:GetHealthCheck"
              ]
              Resource = "*"
              # Note: Service Discovery may require Route53 permissions even for
              # private DNS namespaces with custom health checks
            }
    ]
  })
}

# EventBridge Rule: ECS Task Started
resource "aws_cloudwatch_event_rule" "ecs_task_started" {
  name        = "${var.app_name}-ecs-task-started"
  description = "Trigger when ECS task starts for service discovery registration"

  event_pattern = jsonencode({
    source      = ["aws.ecs"]
    detail-type = ["ECS Task State Change"]
    detail = {
      clusterArn = [aws_ecs_cluster.main.arn]
      lastStatus = ["RUNNING"]
      desiredStatus = ["RUNNING"]
      group = ["service:${aws_ecs_service.backend.name}"]
    }
  })

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# EventBridge Rule: ECS Task Stopped
resource "aws_cloudwatch_event_rule" "ecs_task_stopped" {
  name        = "${var.app_name}-ecs-task-stopped"
  description = "Trigger when ECS task stops for service discovery deregistration"

  event_pattern = jsonencode({
    source      = ["aws.ecs"]
    detail-type = ["ECS Task State Change"]
    detail = {
      clusterArn = [aws_ecs_cluster.main.arn]
      lastStatus = ["STOPPED"]
      group = ["service:${aws_ecs_service.backend.name}"]
    }
  })

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# EventBridge Targets
resource "aws_cloudwatch_event_target" "register_lambda" {
  rule      = aws_cloudwatch_event_rule.ecs_task_started.name
  target_id = "RegisterServiceDiscoveryInstance"
  arn       = aws_lambda_function.service_discovery_register.arn
}

resource "aws_cloudwatch_event_target" "deregister_lambda" {
  rule      = aws_cloudwatch_event_rule.ecs_task_stopped.name
  target_id = "DeregisterServiceDiscoveryInstance"
  arn       = aws_lambda_function.service_discovery_deregister.arn
}

# Lambda Permissions for EventBridge
resource "aws_lambda_permission" "register_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.service_discovery_register.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ecs_task_started.arn
}

resource "aws_lambda_permission" "deregister_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.service_discovery_deregister.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ecs_task_stopped.arn
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "lambda_service_discovery_register" {
  name              = "/aws/lambda/${var.app_name}-service-discovery-register"
  retention_in_days = 7

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

resource "aws_cloudwatch_log_group" "lambda_service_discovery_deregister" {
  name              = "/aws/lambda/${var.app_name}-service-discovery-deregister"
  retention_in_days = 7

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}


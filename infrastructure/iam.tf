# IAM Roles and Policies for Church Course Tracker

# ECS Execution Role
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.app_name}-ecs-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# ECS Execution Role Policy
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.app_name}-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# S3 Access Policy for ECS Tasks
resource "aws_iam_policy" "s3_access_policy" {
  name        = "${var.app_name}-s3-access"
  description = "Policy for S3 access from ECS tasks"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.uploads.arn,
          "${aws_s3_bucket.uploads.arn}/*"
        ]
      }
    ]
  })
}

# Attach S3 policy to ECS task role
resource "aws_iam_role_policy_attachment" "ecs_task_s3_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# Secrets Manager Access Policy
resource "aws_iam_policy" "secrets_manager_policy" {
  name        = "${var.app_name}-secrets-manager"
  description = "Policy for Secrets Manager access from ECS tasks"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.app_secrets.arn
        ]
      }
    ]
  })
}

# Attach Secrets Manager policy to ECS task role
resource "aws_iam_role_policy_attachment" "ecs_task_secrets_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.secrets_manager_policy.arn
}

# CloudWatch Logs Policy
resource "aws_iam_policy" "cloudwatch_logs_policy" {
  name        = "${var.app_name}-cloudwatch-logs"
  description = "Policy for CloudWatch Logs access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          "${aws_cloudwatch_log_group.backend.arn}:*"
        ]
      }
    ]
  })
}

# Attach CloudWatch Logs policy to ECS execution role
resource "aws_iam_role_policy_attachment" "ecs_execution_cloudwatch_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.cloudwatch_logs_policy.arn
}

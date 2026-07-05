# ECS Configuration for Church Course Tracker

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"  # Disabled to reduce CloudWatch costs
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.app_name}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${aws_ecr_repository.backend.repository_url}:latest"

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "AWS_S3_BUCKET"
          value = aws_s3_bucket.uploads.bucket
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        }
      ]

      # DATABASE_URL was previously injected here as a plaintext env var by
      # interpolating var.db_password directly into the ECS task definition.
      # That made the password visible in:
      #   - the ECS console (task definition env vars are plain text in the UI)
      #   - terraform.tfvars (where db_password is set)
      #   - terraform plan/apply output
      # As of 2026-05-09 the full DATABASE_URL is sourced from Secrets Manager
      # via the secrets[] block below. The Secrets Manager value is the single
      # source of truth; var.db_password is no longer used by the ECS task.
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:DATABASE_URL::"
        },
        {
          name      = "SECRET_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:SECRET_KEY::"
        },
        {
          name      = "PLANNING_CENTER_APP_ID"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:PLANNING_CENTER_APP_ID::"
        },
        {
          name      = "PLANNING_CENTER_SECRET"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:PLANNING_CENTER_SECRET::"
        },
        {
          name      = "ADMIN_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:ADMIN_PASSWORD::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  # deploy.yml registers a new revision of this family on every deploy,
  # pinned to the SHA-tagged image (the :latest reference above is
  # bootstrap-only and stale). Ignore drift so terraform apply doesn't
  # register a competing revision. To change env vars/secrets/resources
  # here: edit, temporarily comment out this lifecycle block, apply, then
  # let the next CI deploy re-pin the image.
  lifecycle {
    ignore_changes = [container_definitions]
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# ECS Service (without load balancer, using service discovery)
resource "aws_ecs_service" "backend" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.min_capacity
  launch_type     = "FARGATE"

  # CI (deploy.yml) points the service at each new SHA-pinned task
  # definition revision; don't let terraform apply roll it back to the
  # bootstrap revision.
  lifecycle {
    ignore_changes = [task_definition]
  }

  # Moved to public subnets 2026-05-26 to eliminate the need for NAT egress
  # (private subnets had no working NAT) and the 4 interface VPC endpoints.
  # Inbound on port 8000 is still gated by the SG, which only allows the
  # API Gateway VPC Link SG and intra-VPC sources - the public IP is for
  # egress to ECR/Secrets Manager/CloudWatch Logs only.
  network_configuration {
    security_groups  = [aws_security_group.ecs.id]
    subnets          = module.vpc.public_subnets
    assign_public_ip = true
  }

  # ECS-native Service Discovery registration. Restored 2026-05-09 after the
  # Lambda-based register path silently broke (last invocation Feb 12, 2026),
  # leaving running tasks unregistered and the site routable only by stale
  # entries that aged out. ECS handles register/deregister on task lifecycle
  # transitions; the EventBridge-triggered Lambdas (church-course-tracker-
  # service-discovery-register / -deregister) are now redundant and should be
  # retired in a follow-up. The earlier concern about "health status being
  # overwritten" (see prior comment in git history) is mitigated because the
  # backend SD service has no HealthCheckCustomConfig, so AWS sets the default
  # health status only on register and ECS does not subsequently overwrite it.
  service_registries {
    registry_arn   = aws_service_discovery_service.backend.arn
    container_name = "backend"
    container_port = 8000
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Auto Scaling Target
resource "aws_appautoscaling_target" "backend" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy - CPU
resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "${var.app_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.cpu_target_value

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

# Auto Scaling Policy - Memory
resource "aws_appautoscaling_policy" "backend_memory" {
  name               = "${var.app_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.memory_target_value

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
  }
}

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
          name  = "DATABASE_URL"
          value = "postgresql://postgres:${var.db_password}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/church_course_tracker"
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

      secrets = [
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

  network_configuration {
    security_groups  = [aws_security_group.ecs.id]
    subnets          = module.vpc.private_subnets
    assign_public_ip = false
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

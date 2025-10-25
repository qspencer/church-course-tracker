# API Gateway HTTP API for Church Course Tracker
# Replaces ALB to save ~$15/month in costs

# VPC Link to connect API Gateway to ECS in private subnets
resource "aws_apigatewayv2_vpc_link" "main" {
  name               = "${var.app_name}-vpc-link"
  security_group_ids = [aws_security_group.api_gateway_vpc_link.id]
  subnet_ids         = module.vpc.private_subnets

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.app_name}-api"
  protocol_type = "HTTP"
  description   = "API Gateway for Church Course Tracker Backend"

  cors_configuration {
    allow_origins = ["https://apps.quentinspencer.com", "http://localhost:4200"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    allow_headers = ["*"]
    max_age       = 3600
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Service Discovery for ECS tasks
resource "aws_service_discovery_private_dns_namespace" "main" {
  name        = "${var.app_name}.local"
  description = "Service discovery namespace for ${var.app_name}"
  vpc         = module.vpc.vpc_id

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

resource "aws_service_discovery_service" "backend" {
  name = "backend"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 3
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# API Gateway Integration with VPC Link
resource "aws_apigatewayv2_integration" "backend" {
  api_id             = aws_apigatewayv2_api.main.id
  integration_type   = "HTTP_PROXY"
  integration_method = "ANY"
  integration_uri    = "arn:aws:elasticloadbalancing:us-east-1:334581603621:listener/app/church-course-tracker-alb-v2/e6311536feb13363/4d31f2e6fde3c2ff"
  connection_type    = "VPC_LINK"
  connection_id      = aws_apigatewayv2_vpc_link.main.id

  request_parameters = {
    "overwrite:path" = "$request.path"
  }
}

# Default route (catch-all)
resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.backend.id}"
}

# Specific route for API
resource "aws_apigatewayv2_route" "api" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "ANY /api/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.backend.id}"
}

# Health check route
resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.backend.id}"
}

# API Gateway Stage
resource "aws_apigatewayv2_stage" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      integrationError = "$context.integrationErrorMessage"
    })
  }

  default_route_settings {
    throttling_burst_limit = 5000
    throttling_rate_limit  = 10000
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Custom domain for API Gateway
resource "aws_apigatewayv2_domain_name" "main" {
  domain_name = "api.quentinspencer.com"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate_validation.api_quentinspencer_com.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# API Gateway domain mapping
resource "aws_apigatewayv2_api_mapping" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  domain_name = aws_apigatewayv2_domain_name.main.id
  stage       = aws_apigatewayv2_stage.main.id
}

# Security group for VPC Link
resource "aws_security_group" "api_gateway_vpc_link" {
  name_prefix = "${var.app_name}-vpc-link-"
  vpc_id      = module.vpc.vpc_id
  description = "Security group for API Gateway VPC Link"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.app_name}"
  retention_in_days = 7

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}


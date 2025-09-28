# AWS Infrastructure for Church Course Tracker
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables are defined in variables.tf

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.8.0"
  
  name = "${var.app_name}-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# RDS PostgreSQL Database (Cost-optimized for development)
resource "aws_db_instance" "main" {
  identifier = "${var.app_name}-db"
  
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.t3.micro"  # Smallest instance for cost optimization
  
  allocated_storage     = 20
  max_allocated_storage = 50  # Reduced for cost optimization
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = "church_course_tracker"
  username = "postgres"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 3  # Reduced for cost optimization
  backup_window         = "03:00-04:00"
  maintenance_window    = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true  # For development
  deletion_protection = false  # For development
  
  # Cost optimization settings
  performance_insights_enabled = false
  monitoring_interval = 0
  monitoring_role_arn = null
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# S3 Bucket for file uploads
resource "aws_s3_bucket" "uploads" {
  bucket = "${var.app_name}-uploads-${random_string.bucket_suffix.result}"
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket for static website
resource "aws_s3_bucket" "static_website" {
  bucket = "${var.app_name}-static-${random_string.bucket_suffix.result}"
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# S3 Bucket Policy for CloudFront access
resource "aws_s3_bucket_policy" "static_website" {
  bucket = aws_s3_bucket.static_website.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontOriginAccessIdentity"
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.main.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.static_website.arn}/*"
      }
    ]
  })
}

# ECR Repository for backend
resource "aws_ecr_repository" "backend" {
  name                 = "${var.app_name}-backend"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_s3_bucket.static_website.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.static_website.id}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.main.cloudfront_access_identity_path
    }
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.static_website.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  
  price_class = "PriceClass_100"
  
  aliases = ["apps.quentinspencer.com"]
  
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.apps_quentinspencer_com.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  # Custom error pages for Angular SPA routing
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# ECS Cluster is defined in ecs.tf

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# ALB Target Group
resource "aws_lb_target_group" "backend" {
  name        = "cct-backend-tg-v2"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# ALB HTTP Listener (redirects to HTTPS)
resource "aws_lb_listener" "backend_http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ALB HTTPS Listener
resource "aws_lb_listener" "backend_https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate_validation.api_quentinspencer_com.certificate_arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# ALB Listener Rule for API routing
resource "aws_lb_listener_rule" "api_rule" {
  listener_arn = aws_lb_listener.backend_https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# Security Groups
resource "aws_security_group" "alb" {
  name_prefix = "${var.app_name}-alb-"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
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

resource "aws_security_group" "ecs" {
  name_prefix = "${var.app_name}-ecs-"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
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

resource "aws_security_group" "rds" {
  name_prefix = "${var.app_name}-rds-"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Database subnet group
resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = module.vpc.private_subnets
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# CloudFront Origin Access Identity
resource "aws_cloudfront_origin_access_identity" "main" {
  comment = "OAI for ${var.app_name}"
}

# Route 53 Hosted Zone for quentinspencer.com
resource "aws_route53_zone" "quentinspencer_com" {
  name = "quentinspencer.com"
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# SSL Certificate for apps.quentinspencer.com
resource "aws_acm_certificate" "apps_quentinspencer_com" {
  domain_name       = "apps.quentinspencer.com"
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# SSL Certificate for api.quentinspencer.com
resource "aws_acm_certificate" "api_quentinspencer_com" {
  domain_name       = "api.quentinspencer.com"
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Certificate validation for apps.quentinspencer.com
resource "aws_route53_record" "apps_quentinspencer_com_validation" {
  for_each = {
    for dvo in aws_acm_certificate.apps_quentinspencer_com.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.quentinspencer_com.zone_id
}

# Certificate validation for api.quentinspencer.com
resource "aws_route53_record" "api_quentinspencer_com_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api_quentinspencer_com.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.quentinspencer_com.zone_id
}

# Certificate validation completion for apps.quentinspencer.com
resource "aws_acm_certificate_validation" "apps_quentinspencer_com" {
  certificate_arn         = aws_acm_certificate.apps_quentinspencer_com.arn
  validation_record_fqdns = [for record in aws_route53_record.apps_quentinspencer_com_validation : record.fqdn]
  
  timeouts {
    create = "10m"
  }
}

# Certificate validation completion for api.quentinspencer.com
resource "aws_acm_certificate_validation" "api_quentinspencer_com" {
  certificate_arn         = aws_acm_certificate.api_quentinspencer_com.arn
  validation_record_fqdns = [for record in aws_route53_record.api_quentinspencer_com_validation : record.fqdn]
  
  timeouts {
    create = "10m"
  }
}

# Route 53 A record for apps.quentinspencer.com pointing to CloudFront
resource "aws_route53_record" "apps_quentinspencer_com" {
  zone_id = aws_route53_zone.quentinspencer_com.zone_id
  name    = "apps.quentinspencer.com"
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route 53 A record for api.quentinspencer.com pointing to ALB
resource "aws_route53_record" "api_quentinspencer_com" {
  zone_id = aws_route53_zone.quentinspencer_com.zone_id
  name    = "api.quentinspencer.com"
  type    = "A"
  
  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

# Variables are defined in variables.tf

# Outputs are defined in outputs.tf

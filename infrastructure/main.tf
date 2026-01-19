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
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
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
  
  # Use NAT instance instead of NAT Gateway for cost savings
  enable_nat_gateway = false
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
  engine_version = "15.12"
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

# S3 Bucket Versioning (optional, for rollback capability)
resource "aws_s3_bucket_versioning" "static_website" {
  bucket = aws_s3_bucket.static_website.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Public Access Block (restrict public access, CloudFront uses OAI)
resource "aws_s3_bucket_public_access_block" "static_website" {
  bucket = aws_s3_bucket.static_website.id
  
  block_public_acls       = true
  block_public_policy      = true
  ignore_public_acls      = true
  restrict_public_buckets = true
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
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.static_website.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    # Use modern cache policy approach (recommended)
    # For hashed files (JS/CSS with content hash), cache for 1 year
    # CloudFront will respect Cache-Control headers from S3
    min_ttl     = 0
    default_ttl = 86400  # 1 day default (will be overridden by Cache-Control headers)
    max_ttl     = 31536000  # 1 year max (for hashed files)
    
    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
      cookies {
        forward = "none"
      }
    }
  }
  
  # Cache behavior for index.html (never cache, always fetch fresh)
  ordered_cache_behavior {
    path_pattern     = "index.html"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.static_website.id}"
    compress         = true
    viewer_protocol_policy = "redirect-to-https"
    
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
    
    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
      cookies {
        forward = "none"
      }
    }
  }
  
  # Cache behavior for hashed assets (JS/CSS with content hash) - cache long-term
  ordered_cache_behavior {
    path_pattern     = "*.js"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.static_website.id}"
    compress         = true
    viewer_protocol_policy = "redirect-to-https"
    
    min_ttl     = 31536000  # 1 year
    default_ttl = 31536000  # 1 year
    max_ttl     = 31536000  # 1 year
    
    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
      cookies {
        forward = "none"
      }
    }
  }
  
  ordered_cache_behavior {
    path_pattern     = "*.css"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.static_website.id}"
    compress         = true
    viewer_protocol_policy = "redirect-to-https"
    
    min_ttl     = 31536000  # 1 year
    default_ttl = 31536000  # 1 year
    max_ttl     = 31536000  # 1 year
    
    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
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
    response_page_path = "/churchcoursetracker/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/churchcoursetracker/index.html"
  }
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# ECS Cluster is defined in ecs.tf
# API Gateway is defined in api_gateway.tf (replaces ALB for cost savings)

# Security Groups
resource "aws_security_group" "ecs" {
  name_prefix = "${var.app_name}-ecs-"
  vpc_id      = module.vpc.vpc_id
  description = "Security group for ECS tasks"
  
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.api_gateway_vpc_link.id]
    description     = "Allow traffic from API Gateway VPC Link"
  }
  
  # Allow Service Discovery HTTP health checks from within VPC
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
    description = "Allow Service Discovery health checks from within VPC"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
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

# Security Group for NAT Instances
resource "aws_security_group" "nat_instance" {
  name_prefix = "${var.app_name}-nat-instance-"
  vpc_id      = module.vpc.vpc_id
  description = "Security group for NAT instances"
  
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["10.0.1.0/24", "10.0.2.0/24"]  # Private subnet CIDR blocks
    description = "Allow traffic from private subnets"
  }
  
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "udp"
    cidr_blocks = ["10.0.1.0/24", "10.0.2.0/24"]  # Private subnet CIDR blocks
    description = "Allow UDP traffic from private subnets"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = {
    Name        = "${var.app_name}-nat-instance-sg"
    Environment = var.environment
    Application = var.app_name
  }
}

# Data source to get the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "state"
    values = ["available"]
  }
}

# NAT Instances (one per availability zone)
resource "aws_instance" "nat" {
  count = length(module.vpc.public_subnets)
  
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.nat_instance_type
  subnet_id              = module.vpc.public_subnets[count.index]
  vpc_security_group_ids = [aws_security_group.nat_instance.id]
  source_dest_check      = false  # Required for NAT functionality
  associate_public_ip_address = true
  
  user_data = <<-EOF
              #!/bin/bash
              # Enable IP forwarding immediately
              echo 1 > /proc/sys/net/ipv4/ip_forward

              # Make IP forwarding persistent across reboots
              cat >> /etc/sysctl.d/99-nat.conf << 'SYSCTL'
              net.ipv4.ip_forward = 1
              SYSCTL
              sysctl -p /etc/sysctl.d/99-nat.conf

              # Configure iptables for NAT
              iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

              # Install iptables-services for persistence (Amazon Linux 2)
              yum install -y iptables-services
              systemctl enable iptables
              systemctl start iptables

              # Save iptables rules
              iptables-save > /etc/sysconfig/iptables

              # Create a systemd service to restore NAT on boot (backup method)
              cat > /etc/systemd/system/nat-setup.service << 'SERVICE'
              [Unit]
              Description=NAT Instance Setup
              After=network.target

              [Service]
              Type=oneshot
              ExecStart=/bin/bash -c 'echo 1 > /proc/sys/net/ipv4/ip_forward && iptables -t nat -C POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE'
              RemainAfterExit=yes

              [Install]
              WantedBy=multi-user.target
              SERVICE

              systemctl daemon-reload
              systemctl enable nat-setup.service
              EOF
  
  tags = {
    Name        = "${var.app_name}-nat-instance-${count.index + 1}"
    Environment = var.environment
    Application = var.app_name
  }
}

# Get the primary network interface for each NAT instance
data "aws_network_interface" "nat" {
  count = length(aws_instance.nat)
  
  id = aws_instance.nat[count.index].primary_network_interface_id
}

# Update private route tables to use NAT instances instead of NAT Gateway
resource "aws_route" "private_nat" {
  count = length(module.vpc.private_route_table_ids)
  
  route_table_id         = module.vpc.private_route_table_ids[count.index]
  destination_cidr_block = "0.0.0.0/0"
  network_interface_id   = data.aws_network_interface.nat[count.index].id
  
  depends_on = [aws_instance.nat]
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
    create = "45m"
  }
}

# Certificate validation completion for api.quentinspencer.com
resource "aws_acm_certificate_validation" "api_quentinspencer_com" {
  certificate_arn         = aws_acm_certificate.api_quentinspencer_com.arn
  validation_record_fqdns = [for record in aws_route53_record.api_quentinspencer_com_validation : record.fqdn]
  
  timeouts {
    create = "45m"
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

# Route 53 A record for api.quentinspencer.com pointing to API Gateway
resource "aws_route53_record" "api_quentinspencer_com" {
  zone_id = aws_route53_zone.quentinspencer_com.zone_id
  name    = "api.quentinspencer.com"
  type    = "A"
  
  alias {
    # API Gateway custom domain endpoint
    name                   = aws_apigatewayv2_domain_name.main.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.main.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

# VPC Endpoints for AWS Services (reduces NAT dependency and improves reliability)
# Security Group for VPC Endpoints
resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "${var.app_name}-vpc-endpoints-"
  vpc_id      = module.vpc.vpc_id
  description = "Security group for VPC endpoints"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
    description = "Allow HTTPS from VPC"
  }

  tags = {
    Name        = "${var.app_name}-vpc-endpoints-sg"
    Environment = var.environment
    Application = var.app_name
  }
}

# Secrets Manager VPC Endpoint
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name        = "${var.app_name}-secretsmanager-endpoint"
    Environment = var.environment
    Application = var.app_name
  }
}

# ECR API VPC Endpoint
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name        = "${var.app_name}-ecr-api-endpoint"
    Environment = var.environment
    Application = var.app_name
  }
}

# ECR DKR VPC Endpoint (for docker pull)
resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name        = "${var.app_name}-ecr-dkr-endpoint"
    Environment = var.environment
    Application = var.app_name
  }
}

# S3 VPC Endpoint (Gateway type, required for ECR image layers)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = module.vpc.private_route_table_ids

  tags = {
    Name        = "${var.app_name}-s3-endpoint"
    Environment = var.environment
    Application = var.app_name
  }
}

# CloudWatch Logs VPC Endpoint (for container logs)
resource "aws_vpc_endpoint" "logs" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name        = "${var.app_name}-logs-endpoint"
    Environment = var.environment
    Application = var.app_name
  }
}

# Variables are defined in variables.tf

# Outputs are defined in outputs.tf

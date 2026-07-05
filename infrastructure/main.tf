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

  # Applied to every taggable resource so tagging can't drift per-resource.
  # Resources keep their explicit tags too (explicit wins on conflict).
  default_tags {
    tags = {
      Environment = var.environment
      Application = var.app_name
      ManagedBy   = "terraform"
    }
  }
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
  
  engine = "postgres"
  # RDS auto-applies minor upgrades, so the running minor version drifts
  # ahead of any exact pin (a stale pin of 15.12 nearly caused a downgrade
  # attempt in July 2026). Pin what is live and ignore minor-version drift;
  # major upgrades are a deliberate edit to both this value and the
  # ignore_changes below.
  engine_version = "15.17"
  instance_class = "db.t4g.micro"  # Graviton instance - cheaper and faster than t3
  
  allocated_storage     = 20
  max_allocated_storage = 50  # Reduced for cost optimization
  # gp3 is cheaper than gp2 at this size and gives a fixed 3000 IOPS baseline
  # instead of gp2's size-derived (20 GiB -> 60) IOPS.
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = "church_course_tracker"
  username = "postgres"
  password = random_password.db.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window         = "03:00-04:00"
  maintenance_window    = "sun:04:00-sun:05:00"

  # apply_immediately so password rotation via random_password.db doesn't
  # queue to the next Sunday maintenance window. The trade-off is that any
  # future modify-db-instance change (instance class, engine version, etc.)
  # also applies immediately - acceptable for this small admin site.
  apply_immediately = true

  # This is the live production database: refuse deletion at the API level
  # and always take a final snapshot if it is ever legitimately destroyed.
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.app_name}-db-final"
  deletion_protection       = true
  
  # Cost optimization settings
  performance_insights_enabled = false
  monitoring_interval = 0
  monitoring_role_arn = null

  lifecycle {
    # See the engine_version comment above.
    ignore_changes = [engine_version]
  }

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

# User-uploaded course content is never public - accessed only through the
# authenticated backend. Match the hardening the static-website bucket has.
resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  block_public_acls       = true
  block_public_policy      = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  versioning_configuration {
    status = "Enabled"
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
  name = "${var.app_name}-backend"
  # IMMUTABLE since 2026-07-05: deploys are pinned to SHA tags registered
  # as task-definition revisions by deploy.yml; a tag can never be silently
  # repointed. (The old :latest tag still exists but nothing deploys it.)
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

# Every deploy pushes a new SHA tag; without expiry the repo grows forever.
# 15 images ≈ 15 rollback points, plenty for this deploy cadence.
resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the 15 most recent images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 15
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
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

# NAT instances and their private-subnet 0.0.0.0/0 routes were removed
# 2026-05-26. The Fargate task now runs in public subnets with a public IP
# for egress (see ecs.tf), so private subnets no longer need NAT - only RDS
# and the API Gateway VPC Link ENIs live there, neither needs internet.

# CloudFront Origin Access Identity
resource "aws_cloudfront_origin_access_identity" "main" {
  comment = "OAI for ${var.app_name}"
}

# Route 53 hosted zone for quentinspencer.com is owned by the
# quentinspencer-website repo (zone Z06093453EALOOTL0RHE2, which the registrar
# delegates to). Use a data source here so this stack writes its records into
# the active zone instead of creating a parallel orphan zone that doesn't
# resolve. The previous orphan zone (Z09323901ZY1EPQDTXR7P) was deleted on
# 2026-05-26.
data "aws_route53_zone" "quentinspencer_com" {
  # Pinned to the registrar-delegated zone by id (the same id used in docs.tf
  # for the docs subdomain records). Lookup by name alone is ambiguous while
  # the orphan zone still exists; once it's deleted, this could be switched
  # back to a name lookup if preferred.
  zone_id = "Z06093453EALOOTL0RHE2"
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
  zone_id         = data.aws_route53_zone.quentinspencer_com.zone_id
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
  zone_id         = data.aws_route53_zone.quentinspencer_com.zone_id
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
  zone_id = data.aws_route53_zone.quentinspencer_com.zone_id
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
  zone_id = data.aws_route53_zone.quentinspencer_com.zone_id
  name    = "api.quentinspencer.com"
  type    = "A"
  
  alias {
    # API Gateway custom domain endpoint
    name                   = aws_apigatewayv2_domain_name.main.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.main.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

# S3 VPC Endpoint (Gateway type - FREE, improves S3 access performance)
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

# Interface VPC endpoints (secretsmanager, ecr.api, ecr.dkr, logs) and their
# shared security group were removed 2026-05-26. The Fargate task now egresses
# to those AWS APIs over its public IP via the IGW, eliminating the
# ~$32/mo per-AZ interface endpoint charges.

# Variables are defined in variables.tf

# Outputs are defined in outputs.tf

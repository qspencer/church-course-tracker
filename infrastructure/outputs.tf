# Outputs for Church Course Tracker Infrastructure

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.main.domain_name
}

output "cloudfront_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID"
  value       = aws_cloudfront_distribution.main.hosted_zone_id
}

output "api_gateway_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "api_gateway_domain" {
  description = "API Gateway custom domain name"
  value       = aws_apigatewayv2_domain_name.main.domain_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.backend.name
}

output "s3_uploads_bucket" {
  description = "S3 bucket for file uploads"
  value       = aws_s3_bucket.uploads.bucket
}

output "s3_static_bucket" {
  description = "S3 bucket for static website"
  value       = aws_s3_bucket.static_website.bucket
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "secrets_manager_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.app_secrets.arn
  sensitive   = true
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

# Application URLs
output "application_url" {
  description = "Application URL (CloudFront)"
  value       = "https://apps.quentinspencer.com"
}

output "api_url" {
  description = "API URL (ALB)"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

# Domain information
output "domain_name" {
  description = "Custom domain name"
  value       = "apps.quentinspencer.com"
}

output "nameservers" {
  description = "Route 53 nameservers for domain configuration"
  value       = aws_route53_zone.quentinspencer_com.name_servers
}

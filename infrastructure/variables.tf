# Variables for Church Course Tracker Infrastructure

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "church-course-tracker"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "SSL certificate ARN"
  type        = string
  default     = ""
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 10
}

variable "cpu_target_value" {
  description = "Target CPU utilization for auto-scaling"
  type        = number
  default     = 70
}

variable "memory_target_value" {
  description = "Target memory utilization for auto-scaling"
  type        = number
  default     = 80
}

variable "docs_certificate_arn" {
  description = "ACM certificate ARN for docs.quentinspencer.com (optional, will create if not provided)"
  type        = string
  default     = ""
}

variable "nat_instance_type" {
  description = "EC2 instance type for NAT instance"
  type        = string
  default     = "t3.micro"
}

variable "alert_email" {
  description = "Email address that receives CloudWatch alarm notifications via SNS. Required - no default. Set via terraform.tfvars or TF_VAR_alert_email."
  type        = string

  validation {
    condition     = length(var.alert_email) > 0 && can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.alert_email))
    error_message = "alert_email must be a non-empty, valid email address."
  }
}

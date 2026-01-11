# GitHub Actions OIDC Provider and Role for Documentation Deployment

# OIDC Provider for GitHub Actions
resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",  # GitHub Actions OIDC thumbprint
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"   # Backup thumbprint
  ]

  tags = {
    Name        = "GitHub Actions OIDC Provider"
    Environment = var.environment
    Application = var.app_name
  }
}

# IAM Role for GitHub Actions to deploy documentation
resource "aws_iam_role" "github_actions_docs_deploy" {
  name = "${var.app_name}-github-actions-docs-deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:qspencer/church-course-tracker:*"
          }
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Application = "${var.app_name}-docs"
    Purpose     = "GitHub Actions documentation deployment"
  }
}

# Policy for documentation deployment (S3 and CloudFront)
resource "aws_iam_policy" "github_actions_docs_deploy" {
  name        = "${var.app_name}-github-actions-docs-deploy"
  description = "Policy for GitHub Actions to deploy documentation to S3 and invalidate CloudFront"

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
          aws_s3_bucket.docs.arn,
          "${aws_s3_bucket.docs.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation",
          "cloudfront:ListInvalidations"
        ]
        Resource = [
          "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.docs.id}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudfront:ListDistributions"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "github_actions_docs_deploy" {
  role       = aws_iam_role.github_actions_docs_deploy.name
  policy_arn = aws_iam_policy.github_actions_docs_deploy.arn
}

# Data source for current AWS account ID
data "aws_caller_identity" "current" {}






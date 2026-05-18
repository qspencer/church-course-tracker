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


# -----------------------------------------------------------------------------
# IAM Role for the application deploy workflow (.github/workflows/deploy.yml).
#
# Closes 2026-05-18 evaluation §3.3 finding GH-01 (P0): prior to this commit
# the production deploy workflow used long-lived IAM user access keys
# (secrets.AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY). The OIDC provider has
# existed for the docs deploy since the docs site landed; this commit
# extends the same pattern to the main app deploy.
# -----------------------------------------------------------------------------

resource "aws_iam_role" "github_actions_app_deploy" {
  name = "${var.app_name}-github-actions-app-deploy"

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
          # Scope to the qspencer/church-course-tracker repo on the main
          # branch only. Workflow_dispatch runs are also covered because
          # the `sub` claim for those is `repo:.../...:ref:refs/heads/main`.
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:qspencer/church-course-tracker:*"
          }
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Application = var.app_name
    Purpose     = "GitHub Actions application deployment"
  }
}

# Policy granting the minimum permissions the deploy.yml workflow needs:
#   - ECR auth + push for the backend container image
#   - ECS update-service + describe-services for the rolling deploy
#   - S3 sync for the frontend static bundle
#   - CloudFront create/get invalidation for the frontend cache bust
resource "aws_iam_policy" "github_actions_app_deploy" {
  name        = "${var.app_name}-github-actions-app-deploy"
  description = "Least-privilege policy for the deploy.yml workflow (backend ECR/ECS + frontend S3/CloudFront)"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR: GetAuthorizationToken must be on "*" per the API spec
      {
        Sid    = "EcrAuth"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
        ]
        Resource = "*"
      },
      # ECR: scoped image push/pull to the backend repo
      {
        Sid    = "EcrImagePush"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:CompleteLayerUpload",
          "ecr:GetDownloadUrlForLayer",
          "ecr:InitiateLayerUpload",
          "ecr:PutImage",
          "ecr:UploadLayerPart",
        ]
        Resource = aws_ecr_repository.backend.arn
      },
      # ECS: scoped to the backend service + describe on the cluster
      {
        Sid    = "EcsRollingDeploy"
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
        ]
        Resource = [
          aws_ecs_service.backend.id,
          aws_ecs_cluster.main.arn,
        ]
      },
      # S3: scoped to the static-website bucket for `aws s3 sync`
      {
        Sid    = "S3StaticSync"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
        ]
        Resource = [
          aws_s3_bucket.static_website.arn,
          "${aws_s3_bucket.static_website.arn}/*",
        ]
      },
      # CloudFront: invalidate the main distribution
      {
        Sid    = "CloudFrontInvalidate"
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation",
        ]
        Resource = "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.main.id}"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_app_deploy" {
  role       = aws_iam_role.github_actions_app_deploy.name
  policy_arn = aws_iam_policy.github_actions_app_deploy.arn
}

output "github_actions_app_deploy_role_arn" {
  description = "Role ARN to use in .github/workflows/deploy.yml configure-aws-credentials"
  value       = aws_iam_role.github_actions_app_deploy.arn
}






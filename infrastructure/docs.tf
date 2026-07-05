# Infrastructure for Documentation Site
# Hosts documentation at docs.quentinspencer.com/churchcoursetracker/

# S3 Bucket for documentation site
resource "aws_s3_bucket" "docs" {
  bucket = "docs.quentinspencer.com"
  
  tags = {
    Environment = var.environment
    Application = "${var.app_name}-docs"
    Purpose     = "Documentation site"
  }
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "docs" {
  bucket = aws_s3_bucket.docs.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Public Access Block (restrict public access, CloudFront uses OAI)
resource "aws_s3_bucket_public_access_block" "docs" {
  bucket = aws_s3_bucket.docs.id
  
  block_public_acls       = true
  block_public_policy      = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront Origin Access Identity for documentation
resource "aws_cloudfront_origin_access_identity" "docs" {
  comment = "OAI for ${var.app_name} documentation site"
}

# S3 Bucket Policy for CloudFront access
resource "aws_s3_bucket_policy" "docs" {
  bucket = aws_s3_bucket.docs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontOriginAccessIdentity"
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.docs.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.docs.arn}/*"
      }
    ]
  })
}

# CloudFront Distribution for documentation
resource "aws_cloudfront_distribution" "docs" {
  comment = "Documentation site for ${var.app_name}"

  origin {
    domain_name = aws_s3_bucket.docs.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.docs.id}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.docs.cloudfront_access_identity_path
    }
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  
  # Custom domain
  aliases = ["docs.quentinspencer.com"]
  
  # SSL Certificate (must exist in ACM and be validated)
  # Note: If certificate is still validating, use the certificate ARN directly
  # CloudFront will accept it once validation completes
  viewer_certificate {
    acm_certificate_arn      = var.docs_certificate_arn != "" ? var.docs_certificate_arn : (length(aws_acm_certificate_validation.docs) > 0 ? aws_acm_certificate_validation.docs[0].certificate_arn : aws_acm_certificate.docs[0].arn)
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  # Wait for certificate validation record to be created
  # The certificate will validate automatically once DNS propagates
  depends_on = [aws_route53_record.docs_cert_validation]
  
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.docs.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    # Cache policy for documentation (longer cache for static assets)
    cache_policy_id = aws_cloudfront_cache_policy.docs.id

    # Response headers policy for CORS and security
    response_headers_policy_id = aws_cloudfront_response_headers_policy.docs.id

    # default_root_object only handles "/", not "/subpath/" - rewrite those to
    # append index.html so /churchcoursetracker/ serves /churchcoursetracker/index.html.
    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.docs_index_rewrite.arn
    }
  }
  
  # Cache behavior for index.html (no cache)
  ordered_cache_behavior {
    path_pattern     = "*/index.html"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.docs.id}"
    compress         = true
    viewer_protocol_policy = "redirect-to-https"
    
    cache_policy_id = aws_cloudfront_cache_policy.docs_no_cache.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.docs.id
  }
  
  # Error pages
  custom_error_response {
    error_code         = 404
    response_code      = 404
    response_page_path = "/churchcoursetracker/404.html"
  }
  
  custom_error_response {
    error_code         = 403
    response_code      = 404
    response_page_path = "/churchcoursetracker/404.html"
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  tags = {
    Environment = var.environment
    Application = "${var.app_name}-docs"
  }
}

# CloudFront Function that rewrites subdirectory requests to their index.html.
# Fixes /churchcoursetracker/ returning 404 because CloudFront's
# default_root_object only applies to "/", not arbitrary "/subpath/".
resource "aws_cloudfront_function" "docs_index_rewrite" {
  name    = "${var.app_name}-docs-index-rewrite"
  runtime = "cloudfront-js-1.0"
  comment = "Rewrite /subpath/ and /subpath to /subpath/index.html"
  publish = true
  code    = <<-EOT
    function handler(event) {
      var req = event.request;
      var uri = req.uri;
      if (uri.endsWith('/')) {
        req.uri = uri + 'index.html';
      } else {
        // No extension in the last path segment? Treat as a directory.
        var lastSlash = uri.lastIndexOf('/');
        var lastSegment = uri.slice(lastSlash + 1);
        if (lastSegment.indexOf('.') === -1) {
          req.uri = uri + '/index.html';
        }
      }
      return req;
    }
  EOT
}

# CloudFront Cache Policy for documentation (with longer cache for static assets)
resource "aws_cloudfront_cache_policy" "docs" {
  name        = "${var.app_name}-docs-cache-policy"
  comment     = "Cache policy for documentation site"
  default_ttl = 86400  # 1 day
  max_ttl     = 31536000  # 1 year
  min_ttl     = 0
  
  parameters_in_cache_key_and_forwarded_to_origin {
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip    = true
    
    cookies_config {
      cookie_behavior = "none"
    }
    
    headers_config {
      header_behavior = "none"
    }
    
    query_strings_config {
      query_string_behavior = "none"
    }
  }
}

# CloudFront Cache Policy for index.html (no cache)
# Note: When caching is disabled, accept encoding cannot be enabled
resource "aws_cloudfront_cache_policy" "docs_no_cache" {
  name        = "${var.app_name}-docs-no-cache-policy"
  comment     = "No-cache policy for index.html files"
  default_ttl = 0
  max_ttl     = 0
  min_ttl     = 0
  
  parameters_in_cache_key_and_forwarded_to_origin {
    # Cannot enable accept encoding when caching is disabled
    enable_accept_encoding_brotli = false
    enable_accept_encoding_gzip    = false
    
    cookies_config {
      cookie_behavior = "none"
    }
    
    headers_config {
      header_behavior = "none"
    }
    
    query_strings_config {
      query_string_behavior = "none"
    }
  }
}

# CloudFront Response Headers Policy for security and CORS
resource "aws_cloudfront_response_headers_policy" "docs" {
  name    = "${var.app_name}-docs-headers-policy"
  comment = "Security headers for documentation site"
  
  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains          = true
      preload                     = true
      override                    = true
    }
    content_type_options {
      override = true
    }
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
  }
  
  cors_config {
    access_control_allow_origins {
      items = ["https://apps.quentinspencer.com"]
    }
    access_control_allow_headers {
      items = ["*"]
    }
    access_control_allow_methods {
      items = ["GET", "HEAD", "OPTIONS"]
    }
    access_control_allow_credentials = false
    access_control_max_age_sec       = 3600
    origin_override                   = true
  }
}

# ACM Certificate for docs.quentinspencer.com (if not provided)
resource "aws_acm_certificate" "docs" {
  count = var.docs_certificate_arn == "" ? 1 : 0
  
  domain_name       = "docs.quentinspencer.com"
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Environment = var.environment
    Application = "${var.app_name}-docs"
  }
}

# Route 53 validation records for ACM certificate
resource "aws_route53_record" "docs_cert_validation" {
  for_each = var.docs_certificate_arn == "" ? {
    for dvo in aws_acm_certificate.docs[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = "Z06093453EALOOTL0RHE2"  # Use existing zone (domain points to this zone)
}

# ACM Certificate Validation
resource "aws_acm_certificate_validation" "docs" {
  count = var.docs_certificate_arn == "" ? 1 : 0
  
  certificate_arn         = aws_acm_certificate.docs[0].arn
  validation_record_fqdns = [for record in aws_route53_record.docs_cert_validation : record.fqdn]
  
  timeouts {
    create = "45m"
  }
}

# Route 53 record for docs.quentinspencer.com
# Uses the existing Route 53 zone (domain points to this zone)
resource "aws_route53_record" "docs" {
  zone_id = "Z06093453EALOOTL0RHE2"  # Use existing zone (domain points to this zone)
  name    = "docs.quentinspencer.com"
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.docs.domain_name
    zone_id                = aws_cloudfront_distribution.docs.hosted_zone_id
    evaluate_target_health = false
  }
}


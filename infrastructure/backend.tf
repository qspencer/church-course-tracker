# Remote state backend.
#
# Closes 2026-05-18 evaluation §3.3 finding TF-01 (P0): prior to this commit
# Terraform state lived only at infrastructure/terraform.tfstate on one
# developer workstation, which meant loss of that machine = loss of the
# only copy of every generated secret (including random_password.db's RDS
# master password) and of the entire 119-resource state graph.
#
# The S3 bucket and DynamoDB table are deliberately NOT managed by this
# Terraform module - they would be a chicken-and-egg dependency (a
# resource cannot live in its own state). They were created out-of-band
# via aws CLI on 2026-05-18 with versioning enabled, SSE-AES256
# encryption, and public access blocked:
#
#   aws s3api create-bucket --bucket church-course-tracker-tfstate-334581603621 ...
#   aws s3api put-bucket-versioning --versioning-configuration Status=Enabled ...
#   aws s3api put-bucket-encryption --server-side-encryption-configuration ...
#   aws s3api put-public-access-block --public-access-block-configuration ...
#   aws dynamodb create-table --table-name church-course-tracker-tflock ...
#
# To re-create from scratch, replay the commands above. Both resources
# should be protected from accidental deletion (the bucket has versioning
# which makes recovery possible; the lock table is recreatable in seconds).
terraform {
  backend "s3" {
    bucket         = "church-course-tracker-tfstate-334581603621"
    key            = "prod.tfstate"
    region         = "us-east-1"
    dynamodb_table = "church-course-tracker-tflock"
    encrypt        = true
  }
}

# ============================================================
# S3 Module
#
# Creates the media storage bucket for user-uploaded files
# (profile pictures, project screenshots, certificates, etc.)
#
# The bucket is private — files are accessed through Django
# which generates signed URLs or serves them via the app.
# Public access is blocked at the bucket level.
# ============================================================

resource "aws_s3_bucket" "media" {
  bucket = var.media_bucket_name

  tags = {
    Name = "${var.project_name}-media"
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "media" {
  bucket = aws_s3_bucket.media.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning for file recovery
resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Encrypt all objects at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle rule — delete old versions after 30 days
# Prevents storage costs from accumulating
resource "aws_s3_bucket_lifecycle_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  rule {
    id     = "expire-old-versions"
    status = "Enabled"

     filter {}  

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
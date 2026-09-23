output "bucket_name" {
  description = "Name of the media S3 bucket"
  value       = aws_s3_bucket.media.bucket
}

output "bucket_arn" {
  description = "ARN of the media S3 bucket"
  value       = aws_s3_bucket.media.arn
}

output "bucket_url" {
  description = "S3 bucket URL"
  value       = "https://${aws_s3_bucket.media.bucket}.s3.${var.aws_region}.amazonaws.com"
}
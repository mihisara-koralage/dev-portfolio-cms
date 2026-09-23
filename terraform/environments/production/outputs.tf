# ============================================================
# Outputs
# Printed after terraform apply completes
# Used by GitHub Actions in Phase 9
# ============================================================

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = module.ec2.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = module.ec2.public_dns
}

output "media_bucket_name" {
  description = "S3 bucket name for media files"
  value       = module.s3.bucket_name
}

output "media_bucket_url" {
  description = "S3 bucket URL for media files"
  value       = module.s3.bucket_url
}

output "ssh_command" {
  description = "SSH command to connect to the EC2 instance"
  value       = "ssh -i ~/.ssh/portfolio-cms-key.pem ubuntu@${module.ec2.public_ip}"
}
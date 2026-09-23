output "public_ip" {
  description = "Elastic IP address of the EC2 instance"
  value       = aws_eip.web.public_ip
}

output "public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.web.public_dns
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.web.id
}
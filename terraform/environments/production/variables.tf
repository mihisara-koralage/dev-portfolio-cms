# ============================================================
# Variable Declarations
# All values are set in terraform.tfvars
# ============================================================

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name used as a prefix for all resources"
  type        = string
  default     = "portfolio-cms"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zone" {
  description = "Availability zone for the public subnet"
  type        = string
  default     = "ap-south-1a"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of the EC2 key pair for SSH access"
  type        = string
}

variable "media_bucket_name" {
  description = "S3 bucket name for media file storage"
  type        = string
}

variable "dockerhub_username" {
  description = "Docker Hub username for pulling the production image"
  type        = string
}

variable "docker_image" {
  description = "Full Docker image name including username"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the portfolio (used in Nginx config)"
  type        = string
  default     = ""
}
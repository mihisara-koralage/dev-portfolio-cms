# ============================================================
# Terraform Configuration
# ============================================================
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state backend
  # State is stored in S3 and locked via DynamoDB
  # This means CI/CD and local runs never conflict
  backend "s3" {
    bucket         = "portfolio-cms-terraform-state-mihisara"
    key            = "production/terraform.tfstate"
    region         = "ap-south-1"
    use_lockfile = true
    encrypt        = true
  }
}

# ============================================================
# Provider
# ============================================================
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "portfolio-cms"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

# ============================================================
# Modules
# ============================================================

module "vpc" {
  source = "../../modules/vpc"

  project_name       = var.project_name
  vpc_cidr           = var.vpc_cidr
  availability_zone  = var.availability_zone
}

module "iam" {
  source = "../../modules/iam"

  project_name            = var.project_name
  media_bucket_name       = var.media_bucket_name
}

module "s3" {
  source = "../../modules/s3"

  project_name      = var.project_name
  media_bucket_name = var.media_bucket_name
  aws_region        = var.aws_region
}

module "ec2" {
  source = "../../modules/ec2"

  project_name        = var.project_name
  aws_region          = var.aws_region
  vpc_id              = module.vpc.vpc_id
  public_subnet_id    = module.vpc.public_subnet_id
  key_name            = var.key_name
  instance_type       = var.instance_type
  ec2_instance_profile = module.iam.ec2_instance_profile_name
  dockerhub_username  = var.dockerhub_username
  docker_image        = var.docker_image
  domain_name         = var.domain_name
}
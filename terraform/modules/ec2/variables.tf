variable "project_name" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_id" {
  type = string
}

variable "key_name" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "ec2_instance_profile" {
  type = string
}

variable "dockerhub_username" {
  type = string
}

variable "docker_image" {
  type = string
}

variable "domain_name" {
  type    = string
  default = ""
}
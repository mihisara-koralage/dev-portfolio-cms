# ============================================================
# EC2 Module
#
# Creates:
#   - Security Group (firewall rules)
#   - EC2 instance running Ubuntu 22.04
#   - Elastic IP (static public IP that survives reboots)
#   - User data script (bootstraps Docker on first launch)
# ============================================================

# ── Security Group ────────────────────────────────────────────
resource "aws_security_group" "web" {
  name        = "${var.project_name}-sg"
  description = "Security group for portfolio CMS web server"
  vpc_id      = var.vpc_id

  # HTTP — open to the world
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  # HTTPS — open to the world
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # SSH — restricted to your IP only
  # 0.0.0.0/0 is acceptable for a portfolio project
  # In a real production system, lock this to your IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH"
  }

  # All outbound traffic allowed
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# ── AMI Data Source ───────────────────────────────────────────
# Dynamically fetch the latest Ubuntu 22.04 LTS AMI
# so we don't hardcode AMI IDs that change per region
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical (Ubuntu's AWS account)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── User Data Script ──────────────────────────────────────────
# Runs once on first boot to install Docker and set up the server
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e

    echo "=== Portfolio CMS Bootstrap ==="

    # Update system
    apt-get update -y
    apt-get upgrade -y

    # Install required packages
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        unzip \
        make

    # Install Docker
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) \
        signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    # Add ubuntu user to docker group
    usermod -aG docker ubuntu

    # Enable Docker to start on boot
    systemctl enable docker
    systemctl start docker

    # Install AWS CLI
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
        -o "/tmp/awscliv2.zip"
    unzip /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install

    # Create application directory
    mkdir -p /app
    chown ubuntu:ubuntu /app

    echo "=== Bootstrap complete ==="
    echo "Docker version: $(docker --version)"
    echo "Docker Compose version: $(docker compose version)"
  EOF
}

# ── EC2 Instance ──────────────────────────────────────────────
resource "aws_instance" "web" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = var.public_subnet_id
  vpc_security_group_ids = [aws_security_group.web.id]
  iam_instance_profile   = var.ec2_instance_profile

  user_data = local.user_data

  # Root volume — 20GB is plenty for the OS and Docker images
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-root-volume"
    }
  }

  # Prevent accidental termination
  disable_api_termination = false

  tags = {
    Name = "${var.project_name}-web"
  }

  lifecycle {
    # Don't recreate the instance if the AMI changes
    # (security patches update the AMI ID)
    ignore_changes = [ami, user_data]
  }
}

# ── Elastic IP ────────────────────────────────────────────────
# Gives the instance a static public IP that never changes
# Without this, the IP changes every time the instance restarts
resource "aws_eip" "web" {
  instance = aws_instance.web.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }

  depends_on = [aws_instance.web]
}
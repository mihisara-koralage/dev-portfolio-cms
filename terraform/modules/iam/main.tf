# ============================================================
# IAM Module
#
# Creates an IAM role for the EC2 instance.
# The instance assumes this role automatically — no access
# keys are stored on the server. This is the correct AWS
# pattern for EC2-to-S3 access.
#
# Permissions granted:
#   - S3: read/write to the media bucket only
#   - CloudWatch: push logs and metrics
#   - SSM: allow GitHub Actions to run commands via Session Manager
# ============================================================

# ── IAM Role ─────────────────────────────────────────────────
# The trust policy allows EC2 instances to assume this role
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ec2-role"
  }
}

# ── S3 Media Policy ───────────────────────────────────────────
# Grants access to the media bucket only — not all S3 buckets
resource "aws_iam_policy" "s3_media_policy" {
  name        = "${var.project_name}-s3-media-policy"
  description = "Allow EC2 to read and write to the media S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.media_bucket_name}",
          "arn:aws:s3:::${var.media_bucket_name}/*"
        ]
      }
    ]
  })
}

# ── Attach Policies to Role ───────────────────────────────────
resource "aws_iam_role_policy_attachment" "s3_media" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_media_policy.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ── Instance Profile ──────────────────────────────────────────
# An instance profile is the container that holds the role
# and gets attached to the EC2 instance
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}
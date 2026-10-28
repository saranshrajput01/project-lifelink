# ─── S3 bucket for medical documents (replaces local MinIO) ───
resource "aws_s3_bucket" "documents" {
  bucket = "${local.name}-documents-${data.aws_caller_identity.current.account_id}"
  tags   = { Name = "${local.name}-documents" }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket                  = aws_s3_bucket.documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

data "aws_caller_identity" "current" {}

# ─── RDS PostgreSQL ───
resource "random_password" "db" {
  length  = 24
  special = false
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnets"
  subnet_ids = aws_subnet.private[*].id
  tags       = { Name = "${local.name}-db-subnets" }
}

resource "aws_db_instance" "main" {
  identifier             = "${local.name}-postgres"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  storage_type           = "gp3"
  storage_encrypted      = true
  db_name                = var.db_name
  username               = var.db_username
  password               = random_password.db.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  multi_az               = false # set true for production HA
  skip_final_snapshot    = true  # set false for production
  deletion_protection    = false # set true for production
  tags                   = { Name = "${local.name}-postgres" }
}

# ─── ECR repository for the backend image ───
resource "aws_ecr_repository" "backend" {
  name                 = "${local.name}-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = { Name = "${local.name}-backend" }
}

# ─── Secrets Manager: DB URL + app secrets ───
resource "aws_secretsmanager_secret" "app" {
  name                    = "${local.name}/app-secrets"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql+asyncpg://${var.db_username}:${random_password.db.result}@${aws_db_instance.main.address}:5432/${var.db_name}"
    SECRET_KEY   = random_password.db.result
    GROQ_API_KEY = var.groq_api_key
    S3_BUCKET_NAME = aws_s3_bucket.documents.bucket
    S3_REGION    = var.aws_region
  })
}

terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Optional: store state remotely. Create the bucket + DynamoDB table first,
  # then uncomment and run `terraform init -migrate-state`.
  # backend "s3" {
  #   bucket         = "lifelink-tfstate"
  #   key            = "infra/terraform.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "lifelink-tflock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "LIFELINK"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

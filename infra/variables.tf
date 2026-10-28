variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-south-1" # Mumbai
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Prefix for all resource names"
  type        = string
  default     = "lifelink"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "backend_container_port" {
  description = "Port the backend listens on inside the container"
  type        = number
  default     = 8000
}

variable "backend_cpu" {
  description = "Fargate task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 512
}

variable "backend_desired_count" {
  description = "Number of backend tasks to run"
  type        = number
  default     = 1
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "lifelink_db"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "lifelink"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "enable_nat_gateway" {
  description = "Create a NAT gateway (costly). Disable to run ECS in public subnets for dev."
  type        = bool
  default     = true
}

variable "groq_api_key" {
  description = "Groq API key for the backend (stored in Secrets Manager)"
  type        = string
  default     = ""
  sensitive   = true
}

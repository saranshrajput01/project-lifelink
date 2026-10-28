output "alb_url" {
  description = "Public URL of the backend API (point your frontend/DNS here)"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_repository_url" {
  description = "Push your backend image here"
  value       = aws_ecr_repository.backend.repository_url
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.address
}

output "s3_bucket" {
  description = "Document storage bucket"
  value       = aws_s3_bucket.documents.bucket
}

output "push_image_commands" {
  description = "Run these to build & push the backend image to ECR"
  value = <<-EOT
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.backend.repository_url}
    docker build -t ${aws_ecr_repository.backend.repository_url}:latest ../backend
    docker push ${aws_ecr_repository.backend.repository_url}:latest
    aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.backend.name} --force-new-deployment --region ${var.aws_region}
  EOT
}

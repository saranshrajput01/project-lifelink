# ─── ECS cluster ───
resource "aws_ecs_cluster" "main" {
  name = "${local.name}-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ─── IAM: task execution role (pull image, write logs, read secrets) ───
data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name}-ecs-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_secrets" {
  name = "${local.name}-ecs-secrets"
  role = aws_iam_role.ecs_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [aws_secretsmanager_secret.app.arn]
    }]
  })
}

# ─── IAM: task role (app's own AWS access — S3) ───
resource "aws_iam_role" "ecs_task" {
  name               = "${local.name}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "${local.name}-ecs-task-s3"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.documents.arn,
        "${aws_s3_bucket.documents.arn}/*",
      ]
    }]
  })
}

# ─── CloudWatch log group ───
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.name}-backend"
  retention_in_days = 14
}

# ─── Task definition ───
resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.name}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "backend"
    image     = "${aws_ecr_repository.backend.repository_url}:latest"
    essential = true
    portMappings = [{
      containerPort = var.backend_container_port
      protocol      = "tcp"
    }]
    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "S3_ENDPOINT_URL", value = "" } # empty => use real AWS S3
    ]
    secrets = [
      { name = "DATABASE_URL", valueFrom = "${aws_secretsmanager_secret.app.arn}:DATABASE_URL::" },
      { name = "SECRET_KEY", valueFrom = "${aws_secretsmanager_secret.app.arn}:SECRET_KEY::" },
      { name = "GROQ_API_KEY", valueFrom = "${aws_secretsmanager_secret.app.arn}:GROQ_API_KEY::" },
      { name = "S3_BUCKET_NAME", valueFrom = "${aws_secretsmanager_secret.app.arn}:S3_BUCKET_NAME::" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.backend.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "backend"
      }
    }
  }])
}

# ─── ECS service behind the ALB ───
resource "aws_ecs_service" "backend" {
  name            = "${local.name}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    # Private subnets when NAT is enabled; public (with public IP) otherwise.
    subnets          = var.enable_nat_gateway ? aws_subnet.private[*].id : aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = var.enable_nat_gateway ? false : true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = var.backend_container_port
  }

  depends_on = [aws_lb_listener.http]
}

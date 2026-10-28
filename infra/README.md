# Project LIFELINK — AWS Infrastructure (Terraform)

Infrastructure-as-Code for deploying LIFELINK to AWS. **Nothing here is applied
automatically** — review, set your variables, and `terraform apply` yourself when
your AWS account is ready.

## What this provisions

| Resource | Purpose |
|----------|---------|
| VPC + 2 public + 2 private subnets | Network isolation across 2 AZs |
| Internet Gateway + NAT Gateway | Public/outbound connectivity |
| ECS Fargate cluster + service | Runs the backend container (serverless containers) |
| Application Load Balancer | Public HTTPS entry point → backend |
| RDS PostgreSQL 16 | Managed database (replaces local postgres) |
| S3 bucket | Document storage (replaces local MinIO) |
| ECR repository | Stores the backend Docker image |
| Security Groups | Least-privilege ALB → ECS → RDS |
| Secrets Manager | DB password + app secrets |

> Redis/ElastiCache and CloudFront/frontend are intentionally left as TODO stubs
> to keep the first apply small and cheap. Add them once the core is live.

## Prerequisites

1. AWS account + AWS CLI configured (`aws configure`) — **this is the one step you do.**
2. Terraform >= 1.6 installed (`brew install terraform`).
3. A built backend image pushed to the ECR repo (commands printed as `terraform output`).

## Usage

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars   # then edit values
terraform init
terraform plan        # review — nothing is created yet
terraform apply       # creates real AWS resources (costs money)
```

## Rough cost (ap-south-1, minimal)

- ECS Fargate (0.25 vCPU / 0.5GB, 1 task): ~₹700/mo
- RDS db.t4g.micro: ~₹1100/mo
- ALB: ~₹1500/mo
- NAT Gateway: ~₹2700/mo (biggest line item — drop it for dev by using public subnets)
- S3/ECR: negligible at low volume

Estimate: **~₹5000-6000/mo**. To cut cost for a demo, remove the NAT gateway and run
the ECS task in a public subnet (see comment in `network.tf`).

## Teardown

```bash
terraform destroy
```

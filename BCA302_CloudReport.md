# DESIGNING CLOUD SOLUTIONS FOR AN APPLICATION

## Technical Report — BCA302 Cloud Computing

---

**Project Title:** Project LIFELINK — AI-Powered Predictive & Connected Healthcare Intelligence Platform

**Name:** [Your Name]

**Register Number:** [Your Register Number]

**Class:** BCA — VI Semester

**Course Code:** BCA302-5 (Cloud Computing)

**Submission Date:** July 2026

---

## Table of Contents

1. Project Overview
2. Functional Requirement Analysis
3. Identification of Suitable Cloud Services
4. Selection and Justification of Cloud Service Provider
5. Description of Selected Cloud Services and Features
6. Proposed Cloud Architecture Diagram
7. Security Considerations
8. Conclusion
9. References

---

## 1. Project Overview

### 1.1 Title

Project LIFELINK — AI-Powered Predictive & Connected Healthcare Intelligence Platform

### 1.2 Problem Statement

In the current healthcare landscape, patients accumulate medical records across multiple hospitals, clinics, and diagnostic centres over their lifetime. These records exist in fragmented formats — paper prescriptions, PDF lab reports, handwritten doctor notes — making it extremely difficult for patients to maintain a unified health history. When visiting a new doctor or during emergencies, critical medical information is often unavailable, leading to redundant tests, medication conflicts, and delayed treatment decisions.

Furthermore, most individuals lack the medical expertise to interpret their own health data or assess their risk for chronic diseases like diabetes, cardiovascular conditions, or kidney disease. There is a clear need for an intelligent platform that not only stores and organizes medical records but also extracts meaningful insights and predicts health risks.

### 1.3 Objectives

1. To develop a secure, cloud-hosted platform for storing and managing personal medical records including prescriptions, lab reports, and discharge summaries.
2. To implement AI-powered document processing that extracts structured medical data from uploaded documents using OCR and Natural Language Processing.
3. To generate a chronological health timeline providing patients with a unified view of their medical history.
4. To build machine learning models for predicting risks of cardiovascular disease, diabetes, and chronic kidney disease.
5. To design a scalable, secure cloud architecture using AWS services ensuring high availability and data protection.
6. To implement role-based access control enabling patients, doctors, and administrators to interact according to their privileges.

### 1.4 Target Users

| User Role | Description |
|-----------|-------------|
| Patients | Upload medical records, view health timeline, receive risk predictions, interact with AI assistant |
| Doctors | Access patient records (with consent), review health timelines, validate AI-generated insights |
| Administrators | Oversee user accounts, monitor system health, manage platform-wide settings |

### 1.5 Key Functionalities

| Module | Functionality |
|--------|--------------|
| User Authentication | JWT tokens with role-based access control (patient, doctor, admin) |
| Medical Record Upload | Upload PDF/image files (up to 50 MB) to cloud object storage |
| AI Document Processing | Text extraction via PyMuPDF/OCR + GPT-4o-mini structured extraction |
| Health Timeline | Chronological visualization of all medical events |
| Dashboard & Analytics | Real-time statistics on documents and health metrics |
| User Profile | Blood group, allergies, chronic conditions, emergency contacts |
| Admin Panel | Platform statistics, user management, document oversight |
| Risk Assessment | ML prediction for cardiovascular disease, diabetes, and CKD |
| AI Healthcare Assistant | RAG-based chatbot for personalized health queries |

---

## 2. Functional Requirement Analysis

This section maps the application's functional requirements to cloud resource needs.

### 2.1 Core Module Requirements

| Module | Key Requirements | Cloud Implication |
|--------|-----------------|-------------------|
| Authentication | JWT token issuance, bcrypt hashing (12 rounds), role enforcement | Managed database, secure secret storage, adequate compute |
| Document Storage | Upload files up to 50 MB, organized key structure, pre-signed download URLs | Scalable object storage with high durability |
| AI Processing | PDF text extraction, LLM API calls for structured extraction, async processing | Background task queue, outbound API access, message broker |
| Health Timeline | Chronological events from documents, multiple event types, source linking | Indexed relational database with JSONB support |
| Dashboard | Real-time statistics, aggregation queries | Low-latency cache layer |
| Risk Assessment | XGBoost model inference, SHAP explainability, score storage | ML model hosting endpoint, compute with ML libraries |
| AI Assistant | Vector similarity search, LLM-powered responses, conversation history | Vector database (pgvector), embedding generation |

### 2.2 Non-Functional Requirements

| Requirement | Cloud Implication |
|-------------|-------------------|
| Scalability — 1000+ concurrent users | Auto-scaling compute with load balancer |
| Availability — 99.9% uptime | Multi-AZ deployment with health checks |
| Performance — API response under 500ms | CDN, caching layer, optimized database |
| Security — Healthcare data protection | Encryption at rest/transit, VPC isolation, audit logging |
| Cost Efficiency | Pay-per-use services, right-sized instances |

---

## 3. Identification of Suitable Cloud Services

Based on the functional requirements, the following AWS cloud services have been identified:

| S.No | Cloud Service | Category | Purpose | Project Module |
|------|--------------|----------|---------|----------------|
| 1 | Amazon ECS (Fargate) | Compute | Run containerized backend and frontend services | Backend API, Frontend |
| 2 | Amazon RDS for PostgreSQL | Database | Managed relational database with pgvector extension | All modules (primary data store) |
| 3 | Amazon S3 | Object Storage | Store uploaded medical documents with high durability | Document Upload & Storage |
| 4 | Amazon ElastiCache (Redis) | Cache / Broker | API caching and Celery background task queue | Dashboard, AI Processing |
| 5 | Amazon CloudFront | CDN | Serve frontend static assets globally with low latency | Frontend delivery |
| 6 | AWS Application Load Balancer | Networking | Traffic distribution, path-based routing, SSL termination | Backend, Frontend |
| 7 | Amazon ECR | Container Registry | Store Docker images for deployments | CI/CD Pipeline |
| 8 | AWS Secrets Manager | Security | Store API keys, DB credentials, JWT secrets securely | Authentication, AI Processing |
| 9 | Amazon CloudWatch | Monitoring | Application logs, metrics, alarms, and dashboards | All modules |
| 10 | AWS IAM | Security | Fine-grained service permissions, least-privilege access | All modules |
| 11 | Amazon VPC | Networking | Network isolation, private subnets, security groups | All modules |
| 12 | AWS SageMaker | ML Service | Train and deploy XGBoost risk prediction models | Risk Assessment |
| 13 | AWS Certificate Manager | Security | SSL/TLS certificates for HTTPS | Frontend, API |
| 14 | Amazon Route 53 | DNS | Domain management and DNS routing | All modules |
| 15 | GitHub Actions + ECR | DevOps | Automated CI/CD pipeline | Deployment |

### Service Category Summary

| Category | Services | Count |
|----------|----------|-------|
| Compute | ECS, SageMaker | 2 |
| Storage | S3 | 1 |
| Database | RDS PostgreSQL | 1 |
| Cache | ElastiCache Redis | 1 |
| Networking | ALB, VPC, Route 53, CloudFront | 4 |
| Security | IAM, Secrets Manager, ACM | 3 |
| Monitoring | CloudWatch | 1 |
| DevOps | ECR, GitHub Actions | 2 |

---

## 4. Selection and Justification of Cloud Service Provider

### 4.1 Provider Selected: Amazon Web Services (AWS)

### 4.2 Comparative Analysis

| Criteria | AWS | Azure | GCP |
|----------|-----|-------|-----|
| Container Service | ECS/EKS (mature, native) | AKS (Kubernetes only) | Cloud Run / GKE |
| PostgreSQL + pgvector | RDS (fully supported) | Azure DB for PostgreSQL | Cloud SQL |
| Object Storage | S3 (industry standard) | Blob Storage | Cloud Storage |
| ML Platform | SageMaker (end-to-end) | Azure ML | Vertex AI |
| Healthcare Compliance | HIPAA eligible | HIPAA BAA available | HIPAA compliant |
| India Region | Mumbai, Hyderabad | Pune, Mumbai, Chennai | Mumbai |
| Market Share | 31% (market leader) | 25% | 11% |

### 4.3 Justification

**1. S3 API Compatibility:** The application uses boto3 (AWS SDK) with MinIO for local development. MinIO is S3-compatible, meaning the same code works in production on AWS S3 without modification — zero migration effort.

**2. Mature Container Orchestration:** Amazon ECS with Fargate eliminates server management. The project already has Dockerfiles and a GitHub Actions workflow targeting ECS deployment, making AWS the natural production target.

**3. pgvector Support on RDS:** The RAG-based AI assistant requires vector similarity search. RDS PostgreSQL supports pgvector natively, eliminating the need for a separate vector database service.

**4. HIPAA Compliance:** AWS provides Business Associate Agreements and HIPAA-eligible services across its stack — essential for a healthcare application handling sensitive patient data.

**5. Indian Data Centre:** AWS Mumbai (ap-south-1) ensures low latency for Indian users and supports data residency requirements.

**6. Cost-Effective Scaling:** ECS Fargate (pay per second), S3 (pay per GB), and RDS (right-sized instances) scale costs proportionally with usage. The AWS Free Tier supports initial deployment.

**7. Ecosystem & Documentation:** Largest community, most extensive documentation, and broadest third-party integration support among all cloud providers.

---

## 5. Description of Selected Cloud Services and Features

### 5.1 Amazon ECS with Fargate

Amazon ECS is a fully managed container orchestration service. With Fargate, containers run without managing EC2 instances.

**Features used:** Fargate serverless launch, service auto-scaling (2–4 tasks based on CPU), task definitions for resource allocation, ALB integration for traffic distribution, rolling deployments for zero downtime.

**Project relevance:** FastAPI backend and React/Nginx frontend run as separate ECS services, deployed via GitHub Actions CI/CD pipeline.

### 5.2 Amazon RDS for PostgreSQL

Managed relational database handling provisioning, patching, backup, and failover for PostgreSQL 16.

**Features used:** pgvector extension for vector search, automated daily backups with 35-day point-in-time recovery, Multi-AZ synchronous replication, AES-256 encryption at rest via KMS, read replicas for analytics offloading.

**Project relevance:** Stores all application data — users, profiles, documents metadata, health events, risk assessments, embeddings, and chat history via async SQLAlchemy (asyncpg).

### 5.3 Amazon S3

Object storage with 99.999999999% (11 nines) durability and unlimited capacity.

**Features used:** Prefix-based organization (`patients/{id}/{year}/{month}/filename`), pre-signed URLs for secure temporary access, server-side encryption (SSE-S3), versioning for deletion protection, lifecycle policies for cost optimization.

**Project relevance:** All medical documents (prescriptions, lab reports, discharge summaries) stored via boto3 — identical code used with MinIO locally and S3 in production.

### 5.4 Amazon ElastiCache for Redis

Fully managed Redis with sub-millisecond response times.

**Features used:** Response caching for dashboard statistics, Celery message broker for async document processing, task result backend, Multi-AZ automatic failover.

**Project relevance:** Powers both the caching layer and background task queue for AI document processing workers.

### 5.5 Amazon CloudFront

Global CDN with 450+ edge locations for low-latency content delivery.

**Features used:** Static asset caching (JS, CSS, images), HTTPS enforcement via ACM integration, cache invalidation on deployments, origin failover.

**Project relevance:** Distributes the production React frontend globally; proxies API requests to the ALB.

### 5.6 AWS Application Load Balancer

Layer 7 load balancer with content-based routing.

**Features used:** Path-based routing (`/api/*` → backend, `/*` → frontend), health checks on `/api/v1/health`, SSL termination, WebSocket support.

**Project relevance:** Single entry point distributing traffic between backend and frontend ECS services.

### 5.7 AWS SageMaker

End-to-end machine learning platform for training and deploying models.

**Features used:** Training jobs for XGBoost on healthcare datasets (UCI Heart Disease, Pima Diabetes, CKD), model registry for versioning, real-time inference endpoints, native SHAP explainability.

**Project relevance:** Powers the risk assessment module — trains models and serves predictions that the backend stores with contributing factors and recommendations.

### 5.8 Amazon CloudWatch

Unified monitoring for logs, metrics, and alarms.

**Features used:** Centralized application logs from ECS containers, custom metrics (processing time, success rate), automated alarms via SNS, Container Insights for resource utilization.

**Project relevance:** Provides observability for a healthcare platform where processing failures directly impact patient experience.

### 5.9 Amazon VPC

Logically isolated network with controlled access.

**Features used:** Public/private subnet architecture, security groups (RDS only accepts backend connections), NAT Gateway for outbound API calls (OpenAI), VPC endpoints for S3 private access.

**Project relevance:** Ensures patient data in RDS and S3 is never directly internet-accessible — all access through authenticated application layer.

---

## 6. Proposed Cloud Architecture Diagram

### 6.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET (Users)                         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                        ┌────────▼────────┐
                        │    Route 53     │
                        │     (DNS)       │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   CloudFront    │
                        │  (CDN + HTTPS)  │
                        └────────┬────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────┐
│  VPC (ap-south-1)              │                                 │
│                                │                                 │
│  ┌─── PUBLIC SUBNETS ──────────┼──────────────────────────┐     │
│  │              ┌──────────────▼─────────────┐            │     │
│  │              │  Application Load Balancer │            │     │
│  │              └──────┬────────────┬────────┘            │     │
│  └─────────────────────┼────────────┼─────────────────────┘     │
│                        │ /api/*     │ /*                         │
│  ┌─── PRIVATE SUBNETS ─┼────────────┼─────────────────────┐     │
│  │         ┌───────────▼──┐   ┌────▼──────────────┐      │     │
│  │         │ ECS Fargate  │   │  ECS Fargate      │      │     │
│  │         │ Backend      │   │  Frontend         │      │     │
│  │         │ (FastAPI)    │   │  (React+Nginx)    │      │     │
│  │         └──┬───┬───┬───┘   └───────────────────┘      │     │
│  │            │   │   │                                   │     │
│  │   ┌────────┘   │   └────────────┐                     │     │
│  │   │            │                │                     │     │
│  │   ▼            ▼                ▼                     │     │
│  │ ┌──────┐  ┌──────────┐  ┌────────────┐               │     │
│  │ │ RDS  │  │ElastiCache│  │  S3 Bucket │               │     │
│  │ │Postgres│ │  Redis   │  │ (Documents)│               │     │
│  │ │pgvector│ │          │  │            │               │     │
│  │ │Multi-AZ│ │          │  │            │               │     │
│  │ └──────┘  └──────────┘  └────────────┘               │     │
│  │                                                        │     │
│  │ ┌────────────┐  ┌──────────────┐                      │     │
│  │ │ SageMaker  │  │ NAT Gateway  │                      │     │
│  │ │(ML Models) │  │(OpenAI calls)│                      │     │
│  │ └────────────┘  └──────────────┘                      │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────┐  ┌────────────────┐  ┌─────┐  ┌──────────┐
    │CloudWatch│  │Secrets Manager │  │ IAM │  │   ECR    │
    │(Monitor) │  │ (Credentials)  │  │     │  │(Images)  │
    └──────────┘  └────────────────┘  └─────┘  └──────────┘

    ┌─────────────────────────────────────────────────────┐
    │   CI/CD: GitHub Actions → ECR → ECS Deployment      │
    └─────────────────────────────────────────────────────┘
```

### 6.2 Data Flow

1. **DNS Resolution:** User accesses the platform; Route 53 resolves to CloudFront.
2. **CDN Layer:** CloudFront serves cached static assets; API requests forwarded to ALB.
3. **Load Balancing:** ALB routes `/api/*` to backend, other paths to frontend.
4. **Application:** ECS Fargate runs containerized services in private subnets.
5. **Data Layer:** Backend communicates with RDS (persistent data), ElastiCache (cache + queue), and S3 (file storage).
6. **AI Layer:** Document processing calls OpenAI via NAT Gateway; risk predictions via SageMaker endpoints.
7. **Security:** All inter-service traffic within VPC; Secrets Manager provides credentials; CloudWatch monitors health.

---

## 7. Security Considerations

### 7.1 Authentication

| Mechanism | Implementation |
|-----------|---------------|
| JWT Tokens | Access tokens (HS256, 30-min expiry) and refresh tokens (7-day expiry) |
| Password Hashing | bcrypt with 12 rounds of salting |
| Token Validation | Every API request validates Bearer token; expired tokens return 401 |

### 7.2 Authorization

| Mechanism | Implementation |
|-----------|---------------|
| RBAC | Three roles — patient, doctor, admin — with distinct permissions |
| Endpoint Enforcement | `require_role()` dependency prevents unauthorized access |
| Resource Isolation | Patients access only their own documents; queries filtered by patient_id |

### 7.3 Encryption

| Layer | Mechanism |
|-------|-----------|
| Data in Transit | TLS 1.2/1.3 via ALB + AWS Certificate Manager |
| Database at Rest | AES-256 encryption via AWS KMS |
| Storage at Rest | S3 Server-Side Encryption (SSE-S3) |
| Cache | ElastiCache in-transit encryption + AUTH token |
| Secrets | AWS Secrets Manager with automatic rotation |

### 7.4 Network Security

- VPC isolation — all resources in private network
- Security Groups — RDS only accepts connections from backend ECS (port 5432)
- Private Subnets — ECS, RDS, ElastiCache have no public IP
- NAT Gateway — outbound access without inbound exposure
- VPC Endpoints — S3 accessed via private connection

### 7.5 Backup and Disaster Recovery

| Component | Strategy | Recovery |
|-----------|----------|----------|
| RDS | Automated daily snapshots + continuous logs | Point-in-time recovery (35-day window) |
| S3 | Versioning enabled | Restore any previous version |
| ECS | Task definitions versioned in ECR | Rollback to previous image tag |
| RTO | < 5 minutes (Multi-AZ automated failover) | |
| RPO | < 1 minute (continuous transaction logs) | |

### 7.6 Monitoring

| Tool | Purpose |
|------|---------|
| CloudWatch Logs | Centralized application logs from all ECS containers |
| CloudWatch Alarms | Alerts when error rate > 5% or response time > 2s |
| AWS CloudTrail | Audit log of all AWS API calls — who, what, when |
| ECS Health Checks | ALB probes `/api/v1/health`; unhealthy containers auto-replaced |

---

## 8. Conclusion

This report presented a comprehensive cloud solution design for Project LIFELINK, an AI-powered healthcare platform. Through systematic analysis of functional requirements spanning authentication, document management, AI processing, health timeline, and predictive analytics, 15 appropriate AWS cloud services were identified across compute, storage, database, networking, security, and monitoring categories.

AWS was selected based on S3 API compatibility with the existing codebase, ECS alignment with the Docker-based architecture, pgvector support for the AI assistant, HIPAA compliance for healthcare data, Indian data centre availability, and cost-effective pay-per-use pricing.

The proposed architecture follows a three-tier model within a VPC — CloudFront and ALB in public subnets for user access, ECS Fargate containers in private subnets for application logic, and RDS/ElastiCache/S3 in private subnets for data persistence. Security is enforced through JWT authentication, RBAC authorization, AES-256 encryption, network isolation, automated backups, and comprehensive monitoring.

This cloud-native design enables LIFELINK to scale from development to production while maintaining the security, availability, and performance standards required for healthcare applications.

---

## 9. References

[1] Amazon Web Services, "Amazon Elastic Container Service Documentation," AWS, 2024. [Online]. Available: https://docs.aws.amazon.com/ecs/. [Accessed: Jul. 2026].

[2] Amazon Web Services, "Amazon RDS for PostgreSQL User Guide," AWS, 2024. [Online]. Available: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html. [Accessed: Jul. 2026].

[3] Amazon Web Services, "Amazon S3 User Guide," AWS, 2024. [Online]. Available: https://docs.aws.amazon.com/AmazonS3/latest/userguide/. [Accessed: Jul. 2026].

[4] Amazon Web Services, "AWS Well-Architected Framework — Security Pillar," AWS, 2024. [Online]. Available: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html. [Accessed: Jul. 2026].

[5] P. Mell and T. Grance, "The NIST Definition of Cloud Computing," NIST Special Publication 800-145, Sep. 2011. [Online]. Available: https://csrc.nist.gov/publications/detail/sp/800-145/final. [Accessed: Jul. 2026].

[6] S. Ramírez, "FastAPI — Modern Web Framework for Building APIs with Python," 2024. [Online]. Available: https://fastapi.tiangolo.com/. [Accessed: Jul. 2026].

[7] Amazon Web Services, "AWS HIPAA Compliance," AWS, 2024. [Online]. Available: https://aws.amazon.com/compliance/hipaa-compliance/. [Accessed: Jul. 2026].

[8] Amazon Web Services, "Amazon SageMaker Developer Guide," AWS, 2024. [Online]. Available: https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html. [Accessed: Jul. 2026].

---

*End of Report*

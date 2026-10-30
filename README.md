# 🏥 Project LIFELINK

**AI-Powered Predictive & Connected Healthcare Intelligence Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What is LIFELINK?

LIFELINK is an AI-powered healthcare platform that:

- **Stores** medical records securely (prescriptions, lab reports, discharge summaries)
- **Reads** documents using OCR and extracts structured medical data
- **Organizes** everything into a chronological health timeline
- **Predicts** health risks using ML models trained on real-world medical datasets
- **Assists** patients and doctors with an intelligent AI healthcare assistant

> Designed to compete with global healthcare platforms. Built with enterprise-grade architecture.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend dev)
- Python 3.11+ (for backend dev)

### Run with Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/saranshrajput01/project-lifelink.git
cd project-lifelink

# Start all services (PostgreSQL, Redis, MinIO, Backend, Frontend)
docker compose up -d

# Check status
docker compose ps
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## 🏗️ Architecture

```
project-lifelink/
├── backend/          → FastAPI (Python) — REST API + AI services
├── frontend/         → React + TypeScript + Tailwind CSS
├── scripts/          → Database & utility scripts
├── docs/             → Architecture & API documentation
└── .github/          → CI/CD workflows
```

**Tech Stack:**
| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS, Vite — hosted on **Vercel** |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async) — hosted on **Render** (Docker) |
| Database | PostgreSQL + pgvector — **Supabase** |
| Cache | Redis 7 (local Docker only) |
| Storage | **Supabase Storage** (S3-compatible; MinIO locally) |
| AI/ML | Groq (Qwen LLM), Scikit-learn |
| OCR | PyMuPDF, PaddleOCR (local) |
| DevOps | Docker, GitHub Actions, Vercel + Render auto-deploy |

**Live:** Frontend https://project-lifelink-1.vercel.app · Backend https://lifelink-backend-tunc.onrender.com

---

## 📊 Key Features

| Module | Status |
|--------|--------|
| User Authentication (JWT + RBAC) | ✅ Complete |
| Medical Record Upload & Storage | ✅ Complete |
| AI Document Processing (OCR + NLP) | 🟡 Built (API key needed) |
| Health Timeline Generation | ✅ Complete |
| Dashboard & Analytics | ✅ Complete |
| User Profile Management | ✅ Complete |
| Admin Panel | ✅ Complete |
| CI/CD (GitHub Actions) | ✅ Complete |
| Predictive Analytics (ML Models) | ⬜ Planned |
| AI Healthcare Assistant (RAG) | ⬜ Planned |

---

## 🧪 ML Datasets

Models trained on real-world anonymized healthcare data:
- **MIMIC-IV** — Electronic health records (PhysioNet)
- **UCI Heart Disease** — Cardiovascular risk
- **UCI Diabetes (Pima)** — Diabetes prediction
- **UCI Chronic Kidney Disease** — CKD detection

---

## 👤 Author

**Saransh Rajput**

---

## 📄 License

This project is licensed under the MIT License.

# 📘 Project LIFELINK — Complete Documentation

**AI-Powered Predictive & Connected Healthcare Intelligence Platform**

This document explains **every file, every technology, and why it's used.** Use it
for your presentation, viva, or report.

---

## 1. What is LIFELINK? (one line)

A web app where a patient uploads medical reports (PDF/image) → AI reads & summarises
them → builds a health timeline → predicts disease risk (heart/diabetes/kidney) → and
answers health questions via an AI chatbot grounded in the patient's own records.

---

## 2. Technology Stack — what & why

| Layer | Technology | Why we use it |
|-------|-----------|---------------|
| **Frontend** | React 18 + TypeScript + Vite | Fast, modern SPA; TypeScript catches bugs at compile time; Vite = instant hot reload |
| **Styling** | Tailwind CSS + Framer Motion | Rapid, consistent UI; smooth animations |
| **Backend** | Python 3.11 + FastAPI | Async, auto-generates API docs (Swagger), great for AI/ML integration |
| **Database** | PostgreSQL 16 + pgvector | Reliable SQL DB; pgvector stores AI embeddings for semantic search (RAG) |
| **ORM** | SQLAlchemy 2.0 (async) | Write DB queries in Python, no raw SQL, safe from SQL injection |
| **Migrations** | Alembic | Version-controls DB schema changes |
| **Auth** | JWT + bcrypt (python-jose, passlib) | Stateless secure login; passwords hashed (never stored plain) |
| **Storage** | MinIO (local) / Supabase/S3 (prod) | S3-compatible object storage for uploaded documents |
| **AI / LLM** | Groq (Qwen model) + 7-key rotation | Free, fast LLM for extraction, summaries, chat; keys rotate to beat rate limits |
| **OCR** | PyMuPDF + PaddleOCR | Reads text from PDFs (PyMuPDF) and scanned images/handwriting (PaddleOCR) |
| **Embeddings** | sentence-transformers (MiniLM, 384-dim) | Turns text into vectors for RAG semantic search |
| **ML Models** | scikit-learn GradientBoosting | Disease risk prediction (heart/diabetes/CKD); interpretable, no GPU needed |
| **PDF export** | reportlab | Generates downloadable health report PDFs |
| **Email** | smtplib + Gmail SMTP | Reminder notifications |
| **Containers** | Docker + Docker Compose | One command runs the whole stack identically everywhere |
| **Deploy** | Vercel + Render + Supabase | Free-tier managed hosting, auto-deploy from GitHub |
| **CI/CD** | GitHub Actions | Auto lint/test/build on every push |

---

## 3. Architecture (how data flows)

```
 Browser (React)
      │  REST API calls (/api/v1/...)  with JWT token
      ▼
 FastAPI backend
      ├── Auth (JWT verify)
      ├── Endpoints (documents, chat, predictions, reminders...)
      │
      ├──► PostgreSQL + pgvector   (users, documents, embeddings, risks...)
      ├──► MinIO / S3              (the actual uploaded files)
      ├──► Groq LLM                (extract + summarise + chat)
      ├──► PaddleOCR / PyMuPDF     (read document text)
      ├──► sentence-transformers   (make embeddings for RAG)
      └──► ML models (.joblib)     (risk prediction)
```

---

## 4. BACKEND — file by file

### 4.1 Entry point & config (`app/`)

| File | What it does | Why |
|------|--------------|-----|
| `main.py` | Creates the FastAPI app, sets CORS, registers all routes, starts the reminder scheduler on startup | The front door of the backend — everything boots from here |
| `core/config.py` | Loads all settings from `.env` (DB URL, API keys, SMTP, S3) using Pydantic | One type-safe place for all configuration; no hard-coded secrets |
| `core/database.py` | Sets up the async SQLAlchemy engine + session factory + `Base` | All DB access goes through here; `get_db()` gives each request its own session |
| `core/security.py` | Password hashing (bcrypt) + JWT create/verify | Keeps auth logic in one place; passwords never stored in plain text |
| `core/dependencies.py` | `get_current_user_id()` and `require_role()` — FastAPI dependencies | Protects endpoints: verifies the JWT and enforces patient/doctor/admin roles |

### 4.2 API endpoints (`app/api/v1/`)

| File | What it does | Why |
|------|--------------|-----|
| `router.py` | Combines all endpoint routers into one `api_router` | Single include point for `main.py` |
| `endpoints/auth.py` | Register, login, refresh token, `/me` | User accounts & authentication |
| `endpoints/profile.py` | Get/update patient profile (DOB, blood group, allergies...) | Personal health info |
| `endpoints/documents.py` | Upload, list, download, delete, reprocess, insights | Core feature: medical record management + AI processing trigger |
| `endpoints/chat.py` | AI assistant chat endpoint | RAG chatbot grounded in user's records |
| `endpoints/predictions.py` | Risk scoring: `/cardiovascular`, `/diabetes`, `/ckd`, `/history` | Phase 4 ML disease-risk predictions |
| `endpoints/reminders.py` | CRUD reminders + mark done + email on create | Medicine/appointment reminders |
| `endpoints/family.py` | CRUD family member health profiles | Manage family records under one account |
| `endpoints/admin.py` | Platform stats, user management | Admin panel backend |
| `endpoints/health.py` | `/health` check (returns DB status) | Load balancers & monitoring ping this |

### 4.3 Database models (`app/models/`) — these become SQL tables

| File | Table | Stores |
|------|-------|--------|
| `user.py` | users | Accounts: email, password hash, role |
| `profile.py` | user_profiles | DOB, gender, blood group, allergies, emergency contact |
| `document.py` | medical_documents | Uploaded files + OCR text + AI-extracted data + summaries |
| `embedding.py` | document_embeddings | Text chunks + 384-dim vectors (pgvector) for RAG |
| `chat.py` | chat_sessions / chat_messages | AI conversation history |
| `health_event.py` | health_events | Timeline events (visits, tests, diagnoses) |
| `health_metric.py` | health_metrics | Numeric trends (sugar, BP, cholesterol over time) |
| `risk_assessment.py` | risk_assessments | ML prediction results + explanations |
| `reminder.py` | reminders | Reminders + recurrence + notified flag |
| `family_member.py` | family_members | Family health profiles |

### 4.4 Schemas (`app/schemas/`) — request/response shapes (Pydantic)

| File | Why |
|------|-----|
| `auth.py`, `profile.py`, `document.py`, `reminder.py`, `family_member.py` | Validate incoming JSON and shape outgoing JSON. Keeps the API contract clean and auto-documents it in Swagger. Models = DB; Schemas = API. |

### 4.5 Services (`app/services/`) — the business logic / "brains"

| File | What it does | Why |
|------|--------------|-----|
| `groq_client.py` | Calls the Groq LLM; rotates 7 API keys on rate-limit; model fallback | Reliable free AI even under quota limits |
| `ai_processing.py` | Pipeline: detect PDF/image → OCR (PyMuPDF/PaddleOCR) → Groq extract medications/labs/diagnosis → summary | Turns a raw document into structured medical data |
| `embeddings.py` | Loads MiniLM model; chunks text; makes 384-dim vectors | Foundation for semantic search (RAG) |
| `rag.py` | Indexes document chunks into pgvector; retrieves top-k relevant chunks for a query | Lets the chatbot answer from the user's own records |
| `storage.py` | Upload/download/presigned-URL to MinIO/S3/Supabase (boto3) | Handles the actual files; works across local + cloud |
| `report.py` | Builds a health-summary PDF (reportlab) | "Download health report" feature |
| `email.py` | Sends email via SMTP (graceful if not configured) | Reminder notifications |
| `scheduler.py` | Background asyncio loop: every 60s, emails due reminders, rolls recurring | Makes reminders actually "go off" at their due time |

### 4.6 Machine Learning (`app/ml/`)

| File | What it does | Why |
|------|--------------|-----|
| `train.py` | Trains heart/diabetes (synthetic) + CKD (real UCI data) models → saves `.joblib` | Builds the risk-prediction models |
| `predict.py` | Loads models, scores risk, computes contributing factors + recommendations + explanation | Powers the Risk Dashboard with explainable AI |
| `datasets/ckd.arff` | Real UCI Chronic Kidney Disease dataset (399 rows) | Trains the CKD model on real clinical data |
| `models_store/*.joblib` | Saved trained models (heart, diabetes, ckd) | Loaded at prediction time (no re-training needed) |

---

## 5. FRONTEND — file by file (`frontend/src/`)

| File | What it does |
|------|--------------|
| `main.tsx` | React entry point — mounts the app |
| `App.tsx` | All routes (URL → page), wrapped in auth/role guards |
| `services/api.ts` | Axios client: attaches JWT to every request, auto-refreshes expired tokens |
| `components/ProtectedRoute.tsx` | Blocks unauthenticated users; `RoleRoute` redirects wrong roles |
| `components/DocumentUpload.tsx` | Drag-and-drop file upload with progress |
| `pages/LandingPage.tsx` | Public home page |
| `pages/LoginPage.tsx` / `RegisterPage.tsx` | Auth screens (role-based redirect after login) |
| `pages/DashboardPage.tsx` | Patient home: health score, stats, nav to all features |
| `pages/TimelinePage.tsx` | Chronological medical history |
| `pages/ProfilePage.tsx` | Edit personal/health info |
| `pages/ChatPage.tsx` | AI assistant chat UI |
| `pages/RemindersPage.tsx` | Create/list/complete reminders |
| `pages/FamilyPage.tsx` | Manage family member profiles |
| `pages/RiskPage.tsx` | Disease risk calculator (heart/diabetes/CKD) with explanations |
| `pages/DoctorPage.tsx` | Doctor portal (patient list) |
| `pages/AdminPage.tsx` | Admin panel (platform stats, users) |

---

## 6. Infrastructure & DevOps

| File | What it does | Why |
|------|--------------|-----|
| `docker-compose.yml` | Runs 5 services locally: postgres, redis, minio, backend, frontend | One command (`docker compose up`) = full working stack |
| `backend/Dockerfile` | Builds the backend image (Python + CPU torch + OCR libs) | Reproducible backend container |
| `backend/requirements.txt` | All Python dependencies (pinned versions) | Exact, repeatable installs |
| `backend/alembic/` | DB migration scripts | Evolve the schema safely over time |
| `render.yaml` | Render.com deploy blueprint | Free-tier cloud hosting for the backend |
| `docs/DEPLOY_SUPABASE_RENDER.md` | Step-by-step free deploy guide | Supabase (DB+storage) + Render (backend) |
| `.github/workflows/ci.yml` + `deploy.yml` | GitHub Actions: lint, test, build, deploy | Automated quality checks & delivery |

---

## 7. Key Features (what to demo)

1. **Upload a medical report** → AI reads it (OCR + Groq) → extracts medications, lab values, diagnosis → auto-summary
2. **Health Timeline** → all records in chronological order
3. **AI Chat Assistant** → ask "What is my HbA1c?" → answers from YOUR records (RAG + pgvector)
4. **Risk Prediction** → enter values → ML predicts heart/diabetes/CKD risk + explains why + recommendations
5. **Reminders** → set medicine reminders → email on create + auto-email when due (scheduler)
6. **Family Profiles** → manage family members' health info
7. **PDF Report** → download a full health summary
8. **Role-based access** → patient / doctor / admin dashboards

---

## 8. Security practices used

- Passwords hashed with **bcrypt** (never stored in plain text)
- **JWT** access + refresh tokens for stateless auth
- **Role-based access control** (patient/doctor/admin)
- **SQLAlchemy ORM** → parameterised queries (SQL-injection safe)
- Secrets in `.env` (gitignored), not in code
- S3 presigned URLs (temporary, expiring file access)
- CORS restricted to known frontend origins

---

## 9. Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Patient | saransh@test.com | password123 |
| Doctor | doctor@lifelink.com | password123 |
| Admin | admin@lifelink.com | password123 |

**URLs:** Frontend http://localhost:5173 · API docs http://localhost:8000/docs
**Start:** `docker compose up -d`

---

## 10. Root-level files & folders (project top level)

These sit at the very top of the project (not inside backend/frontend).

| File / Folder | What it is | Why it's there |
|---------------|-----------|----------------|
| `.github/workflows/` | GitHub Actions config — `ci.yml` (lint + test + build on every push) and `deploy.yml` (build & push Docker image) | **CI/CD automation** — every time code is pushed to GitHub, it's automatically checked and built, so bugs are caught early |
| `.kiro/steering/` | Kiro AI assistant config (`token-efficiency.md`) | Project-specific rules for the AI coding assistant used during development — not part of the app itself |
| `backend/` | The FastAPI backend (API, database, AI, ML) | The server-side brain of the app |
| `frontend/` | The React web app | What the user sees and clicks in the browser |
| `docs/` | All project documentation (this file, deploy guide, etc.) | Keeps explanations/guides in one place |
| `scripts/init-db.sql` | SQL that runs once when PostgreSQL first starts | **Enables `pgvector`** (for AI embeddings) and `uuid-ossp` (for unique IDs) in the database automatically |
| `docker-compose.yml` | Defines & links all 5 services (postgres, redis, minio, backend, frontend) | One command (`docker compose up`) starts the entire app stack together |
| `render.yaml` | Render.com deployment blueprint | For deploying the backend to free-tier cloud hosting |
| `.gitignore` | Lists files Git should NOT track (`.env`, `node_modules`, models, secrets) | Keeps secrets and large/generated files out of the GitHub repo |
| `README.md` | Project overview + quick-start | First thing anyone sees on GitHub — what the project is and how to run it |
| `ROADMAP.md` | Phase-by-phase progress tracker + session logs | Shows what's done, what's pending, and the development history |
| `BCA302_CloudReport.docx` / `.md` | College cloud-computing report | Academic submission document (not part of the app) |
| `Cloud_Computing_ESE_LIFELINK.docx` | College ESE report | Academic submission document (not part of the app) |

### Quick note on the two config-y files people ask about

- **`docker-compose.yml`** = the "orchestra conductor." It says: run Postgres here, Redis here,
  MinIO here, backend here, frontend here — and connect them. Without it you'd start 5 things
  by hand. With it: one command.
- **`scripts/init-db.sql`** = runs *once* at first DB startup to switch on `pgvector`
  (the feature that lets us store AI embeddings and do semantic search for the chatbot).


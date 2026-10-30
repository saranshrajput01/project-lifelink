# Deploy LIFELINK — Supabase + Render (free tier)

This is how LIFELINK is deployed: Supabase (DB + storage), Render (backend), Vercel (frontend).

```
Frontend  → Vercel / Netlify   (free)
Backend   → Render.com Docker   (free)
Database  → Supabase Postgres + pgvector  (free)
Storage   → Supabase Storage (S3-compatible)  (free)
```

No code changes needed — everything is driven by environment variables.

---

## Step 1 — Supabase (database + storage)

1. Create a project at https://supabase.com (free). Pick a region (e.g. `ap-south-1` / Singapore).
2. **Enable pgvector:** Supabase SQL Editor → run:
   ```sql
   create extension if not exists vector;
   ```
3. **Get the DB connection string:** Project → Settings → Database → *Connection string* →
   choose **"Session pooler"** (port 5432). It looks like:
   ```
   postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
   ```
   Convert the scheme for our async driver → prefix becomes `postgresql+asyncpg://`:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
   ```
4. **Create the storage bucket:** Storage → New bucket → name it `lifelink-documents` (private).
5. **Get S3-compatible storage creds:** Storage → Settings → *S3 Connection* → enable it. You get:
   - Endpoint: `https://<ref>.supabase.co/storage/v1/s3`
   - Region: (shown there, e.g. `ap-south-1`)
   - Access key ID + Secret access key

> Give Kiro these 5 values and it'll fill them in, or set them yourself in Step 3.

---

## Step 2 — Run DB migrations against Supabase

Once `DATABASE_URL` points at Supabase, apply the schema:

```bash
cd backend
DATABASE_URL="postgresql+asyncpg://postgres.<ref>:<pwd>@...pooler.supabase.com:5432/postgres" \
  alembic upgrade head
# then create the ML prediction / family tables (if not covered by a migration):
#   the app also auto-creates missing tables on first boot via Base.metadata.
```

(Also re-run `python -m app.ml.train` if you want the models present; they ship in the image.)

---

## Step 3 — Backend on Render

1. Push this repo to GitHub.
2. render.com → **New → Blueprint** → select the repo. Render reads `render.yaml`.
3. In the service's **Environment** tab, fill the vars marked `sync: false`:

   | Var | Value |
   |-----|-------|
   | `DATABASE_URL` | the Supabase `postgresql+asyncpg://...` string |
   | `S3_ENDPOINT_URL` | `https://<ref>.supabase.co/storage/v1/s3` |
   | `S3_ACCESS_KEY` | Supabase S3 access key |
   | `S3_SECRET_KEY` | Supabase S3 secret key |
   | `S3_REGION` | e.g. `ap-south-1` |
   | `GROQ_API_KEY` | one of your Groq keys |
   | `SMTP_USER` / `SMTP_PASS` / `SMTP_FROM` | Gmail + app password (optional) |
   | `CORS_ORIGINS` | `["https://<your-frontend>.vercel.app"]` |

4. Deploy. Render builds the Docker image (torch/paddle make the first build slow — be patient).
5. Health check hits `/api/v1/health`. When green, note the service URL:
   `https://lifelink-backend.onrender.com`

> Free tier sleeps on inactivity → first request after idle is slow (cold start). Fine for demos.

---

## Step 4 — Frontend on Vercel/Netlify

1. The frontend calls the API at `/api/v1` (relative). Point it at the Render backend:
   - Easiest: set a build-time `VITE_API_BASE_URL=https://lifelink-backend.onrender.com/api/v1`
     and use it in `src/services/api.ts` (or add a proxy/rewrite).
2. Vercel → New Project → pick repo → root `frontend` → deploy.
3. Put the resulting URL into the backend's `CORS_ORIGINS`.

---

## Notes

- **pgvector**: Supabase supports it natively (Step 1.2) — RAG works unchanged.
- **Storage**: our `boto3` client already uses path-style + s3v4, which Supabase requires.
- **MinIO/local** stays the default for `docker compose` dev; only the deployed env uses Supabase.
- **Cost**: all free tiers. No credit card needed for Supabase/Render/Vercel free plans.

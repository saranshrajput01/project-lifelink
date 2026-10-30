"""Build the ESE submission report for Project LIFELINK.

Uses Cloud_Computing_ESE_LIFELINK.docx only as a formatting template: keeps the
cover page and Sections 1-2, then rewrites Sections 3-11 to describe the cloud
stack actually used (Vercel + Render + Supabase), with SDG Alignment and Cloud
Services Used placed before the Conclusion.

Run from repo root:  python3 docs/make_ese_report.py
"""

import copy
from pathlib import Path

import docx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches  # noqa: E402
from docx.table import _Cell  # noqa: E402
from docx.text.paragraph import Paragraph  # noqa: E402
from docx.text.run import Run  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Cloud_Computing_ESE_LIFELINK.docx"
OUT = ROOT / "TeamNo_LIFELINK_Report.docx"
DIAGRAM = ROOT / "docs" / "lifelink_cloud_architecture.png"


# ─── Architecture diagram ────────────────────────────────────────────────
def draw_diagram():
    fig, ax = plt.subplots(figsize=(11, 7.2))
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 72)
    ax.axis("off")

    def box(x, y, w, h, title, sub, color):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.6", fc=color, ec="#333", lw=1.2
            )
        )
        ax.text(
            x + w / 2,
            y + h - 2.6,
            title,
            ha="center",
            va="center",
            fontsize=10.5,
            weight="bold",
        )
        ax.text(
            x + w / 2,
            y + (h - 4) / 2,
            sub,
            ha="center",
            va="center",
            fontsize=8.3,
            linespacing=1.35,
        )

    def arrow(x1, y1, x2, y2, label="", both=False):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="<|-|>" if both else "-|>", color="#444", lw=1.3
            ),
        )
        if label:
            ax.text(
                (x1 + x2) / 2 + 0.8,
                (y1 + y2) / 2,
                label,
                fontsize=7.8,
                color="#222",
                style="italic",
            )

    box(40, 63, 30, 7, "Users", "Patients · Doctors · Admins (any browser)", "#FFF2CC")
    box(
        36,
        49,
        38,
        9,
        "Vercel (Frontend Hosting)",
        "React + TypeScript SPA\nGlobal edge CDN · automatic HTTPS",
        "#DAE8FC",
    )
    box(
        31,
        29,
        48,
        14,
        "Render (Backend PaaS)",
        "FastAPI in Docker · Singapore region\nJWT auth + RBAC · ML risk models\n"
        "AI assistant · reminder scheduler\nHealth check /api/v1/health",
        "#D5E8D4",
    )
    box(
        2,
        6,
        30,
        13,
        "Supabase PostgreSQL",
        "PostgreSQL 17 + pgvector\nusers, records, timeline,\nreminders, risk scores",
        "#E1D5E7",
    )
    box(
        40,
        6,
        30,
        13,
        "Supabase Storage",
        "S3-compatible private bucket\nlifelink-documents\npre-signed URLs",
        "#E1D5E7",
    )
    box(
        78,
        6,
        30,
        13,
        "External cloud APIs",
        "Groq LLM API (Qwen)\ndocument extraction + chat\nGmail SMTP (reminders)",
        "#F8CECC",
    )
    box(
        84,
        49,
        24,
        13,
        "GitHub",
        "Source repo\nGitHub Actions CI\n(lint · test · build)\nauto-deploy on push",
        "#F5F5F5",
    )

    arrow(55, 63, 55, 58.6, "HTTPS", both=True)
    arrow(55, 49, 55, 43.6, "HTTPS REST + JWT", both=True)
    arrow(40, 29, 17, 19.6, "SQL over TLS (asyncpg)", both=True)
    arrow(55, 29, 55, 19.6, "S3 API (boto3)", both=True)
    arrow(70, 29, 93, 19.6, "HTTPS", both=True)
    arrow(84, 54, 74.6, 54)
    ax.text(79.3, 55.5, "deploy", ha="center", fontsize=7.8, style="italic")
    arrow(90, 49, 79.6, 39, "deploy")

    ax.text(
        55,
        1,
        "Fig. 1 — LIFELINK cloud architecture (Vercel + Render + Supabase)",
        ha="center",
        fontsize=9.5,
        style="italic",
    )
    fig.tight_layout()
    fig.savefig(DIAGRAM, dpi=200)
    plt.close(fig)


# ─── Template + helpers ──────────────────────────────────────────────────
d = docx.Document(SRC)
P = d.paragraphs
H1, H2, BODY, BULLET = P[81], P[70], P[71], P[28]
TOC_ITEM, REF = P[19], P[87]
TPL = {2: d.tables[0], 3: d.tables[2], 4: d.tables[4]}


def set_text(par_el, text, bold_prefix=None):
    """Replace a paragraph element's text, keeping the first run's formatting."""
    p = Paragraph(par_el, None)
    runs = p.runs
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    if bold_prefix:
        runs[0].text = bold_prefix
        runs[0].bold = True
        r2 = copy.deepcopy(runs[0]._r)
        runs[0]._r.addnext(r2)
        rr = Run(r2, p)
        rr.text = text
        rr.bold = False
    else:
        runs[0].text = text
    return par_el


def clone(par, text, **kw):
    return set_text(copy.deepcopy(par._p), text, **kw)


def set_cell(cell, text):
    paras = cell.paragraphs
    for extra in paras[1:]:
        extra._p.getparent().remove(extra._p)
    set_text(paras[0]._p, text)


def make_table(rows):
    tbl = copy.deepcopy(TPL[len(rows[0])]._tbl)
    trs = tbl.findall(qn("w:tr"))
    header_tr, data_tr = trs[0], trs[1]
    for tr in trs:
        tbl.remove(tr)
    for i, row in enumerate(rows):
        tr = copy.deepcopy(header_tr if i == 0 else data_tr)
        tbl.append(tr)
        for tc, val in zip(tr.findall(qn("w:tc")), row):
            set_cell(_Cell(tc, None), val)
    return tbl


def image_par():
    p = d.add_paragraph()
    p.alignment = 1
    p.add_run().add_picture(str(DIAGRAM), width=Inches(6.3))
    el = p._p
    el.getparent().remove(el)
    return el


# ─── Content for Sections 3-11 ───────────────────────────────────────────
def build_sections():
    els = []

    def h1(t):
        els.append(clone(H1, t))

    def h2(t):
        els.append(clone(H2, t))

    def body(t):
        els.append(clone(BODY, t))

    def bullet(t, b=None):
        els.append(clone(BULLET, t, bold_prefix=b))

    def table(rows):
        els.append(make_table(rows))

    # ── 3. Identification of Suitable Cloud Services ──
    h1("3. Identification of Suitable Cloud Services")
    body(
        "Working from the requirements above, the platform needs four things from "
        "the cloud: somewhere to serve the web app, somewhere to run the Python API, "
        "a managed database with vector search, and durable file storage. AI "
        "inference and CI/CD are consumed as external cloud services. The services "
        "chosen for each need are listed below."
    )
    table(
        [
            ["#", "Service", "Category", "Role in the Project"],
            [
                "1",
                "Vercel",
                "PaaS + CDN",
                "Hosts and serves the React frontend over a global edge network",
            ],
            [
                "2",
                "Render Web Service",
                "PaaS (containers)",
                "Runs the FastAPI backend from the project's Dockerfile",
            ],
            [
                "3",
                "Supabase PostgreSQL",
                "DBaaS",
                "Primary relational database, with pgvector for embeddings",
            ],
            [
                "4",
                "Supabase Storage",
                "Object storage",
                "Stores uploaded medical documents in a private bucket",
            ],
            [
                "5",
                "Groq Cloud API",
                "AI inference (SaaS)",
                "LLM for document extraction, summaries and the AI assistant",
            ],
            [
                "6",
                "GitHub + GitHub Actions",
                "DevOps (SaaS)",
                "Source control, CI (lint, test, build) and deploy trigger",
            ],
            [
                "7",
                "Gmail SMTP",
                "Email (SaaS)",
                "Sends medicine and follow-up reminder emails",
            ],
        ]
    )
    h2("Service Category Summary")
    table(
        [
            ["Category", "Services", "Count"],
            ["Compute / Hosting", "Vercel, Render", "2"],
            ["Database", "Supabase PostgreSQL (pgvector)", "1"],
            ["Storage", "Supabase Storage", "1"],
            ["AI", "Groq Cloud API", "1"],
            ["DevOps", "GitHub, GitHub Actions", "1"],
            ["Messaging", "Gmail SMTP", "1"],
        ]
    )

    # ── 4. Selection and Justification ──
    h1("4. Selection and Justification of Cloud Service Provider")
    h2("4.1 Providers Selected: Vercel + Render + Supabase")
    body(
        "Instead of putting everything on one large provider, LIFELINK uses three "
        "specialised platforms: Vercel for the frontend, Render for the backend and "
        "Supabase for the database and file storage. Each has a free tier, deploys "
        "straight from GitHub and needs no server administration."
    )
    h2("4.2 Comparative Analysis")
    table(
        [
            ["Criteria", "Vercel + Render + Supabase", "Single hyperscaler (IaaS)"],
            [
                "Cost for this project",
                "$0 per month on free tiers",
                "Free tier is time-limited; NAT gateway, load balancer and managed "
                "DB are billed",
            ],
            [
                "Setup effort",
                "Connect GitHub repo, set environment variables",
                "Configure networks, subnets, security groups, IAM roles",
            ],
            [
                "PostgreSQL + pgvector",
                "Built into Supabase, enabled with one SQL command",
                "Available, but the instance must be provisioned and sized",
            ],
            [
                "File storage",
                "S3-compatible API, works with the existing boto3 code",
                "Native object storage",
            ],
            [
                "Deployment",
                "Automatic on every push to main",
                "Needs a custom CI/CD pipeline",
            ],
            [
                "Limits",
                "Free backend sleeps after 15 min idle; 512 MB RAM",
                "Few limits, but you pay for them",
            ],
        ]
    )
    h2("4.3 Justification")
    bullet(
        " A student project has no budget. All three platforms run LIFELINK at no "
        "cost.",
        "1. Zero cost:",
    )
    bullet(
        " The backend already had a Dockerfile, so Render builds and runs it "
        "unchanged. Supabase Storage speaks the S3 API, so the boto3 storage code "
        "that used MinIO locally needed only a new endpoint URL and keys.",
        "2. Fits the existing code:",
    )
    bullet(
        " The AI assistant stores document embeddings in a vector column. "
        "Supabase ships PostgreSQL with pgvector, so no separate vector database "
        "is needed.",
        "3. pgvector support:",
    )
    bullet(
        " Patching, TLS certificates, backups of the platform and server "
        "restarts are handled by the providers.",
        "4. Fully managed:",
    )
    bullet(
        " Pushing to the main branch on GitHub redeploys the frontend on Vercel and "
        "the backend on Render automatically.",
        "5. Git-based deployment:",
    )
    bullet(
        " Render's Singapore region is the closest free region to India, keeping "
        "API latency low for Indian users.",
        "6. Region:",
    )

    # ── 5. Description of Services ──
    h1("5. Description of Selected Cloud Services and Features")
    services = [
        (
            "5.1 Vercel",
            "Vercel is a frontend cloud platform that builds static and single-page "
            "apps and serves them from a global edge network.",
            "Features used: Vite build on every push, global CDN caching, automatic "
            "HTTPS certificates, SPA rewrite rule (vercel.json) so deep links such as "
            "/dashboard load correctly, and build-time environment variable "
            "VITE_API_BASE_URL pointing to the backend.",
        ),
        (
            "5.2 Render Web Service",
            "Render is a Platform-as-a-Service that builds a Docker image from the "
            "repository and runs it as a managed web service.",
            "Features used: Docker runtime from backend/Dockerfile, infrastructure "
            "defined in render.yaml (Blueprint), health check on /api/v1/health with "
            "automatic restart, secrets stored as environment variables, auto-deploy "
            "from GitHub, and database migrations (alembic upgrade head) run on every "
            "start.",
        ),
        (
            "5.3 Supabase PostgreSQL",
            "Supabase provides a managed PostgreSQL 17 database with extensions.",
            "Features used: pgvector extension for the document_embeddings table, "
            "connection pooler for the async SQLAlchemy (asyncpg) driver, TLS on all "
            "connections, and the dashboard SQL editor for inspection. It stores "
            "users, profiles, document metadata, health events, risk assessments, "
            "reminders, family profiles and chat history.",
        ),
        (
            "5.4 Supabase Storage",
            "Supabase Storage is object storage with an S3-compatible API.",
            "Features used: private bucket lifelink-documents, per-patient key "
            "structure (patients/{id}/{year}/{month}/file), access through boto3 "
            "with S3 access keys, and time-limited pre-signed URLs for downloads so "
            "files are never public.",
        ),
        (
            "5.5 Groq Cloud API",
            "Groq offers hosted large language models through an OpenAI-compatible "
            "API.",
            "Features used: Qwen model for structured JSON extraction (medications, "
            "diagnoses, lab values) and the AI assistant, with automatic rotation "
            "across several API keys and fallback to other models when a rate limit "
            "is hit. Processing runs as a background task so uploads return in a "
            "few seconds.",
        ),
        (
            "5.6 GitHub Actions",
            "GitHub Actions is GitHub's hosted CI/CD service.",
            "Features used: on every push it runs backend lint (ruff, black) and "
            "tests and the frontend lint and build. Vercel and Render watch the same "
            "branch and redeploy when it changes.",
        ),
    ]
    for title, intro, features in services:
        h2(title)
        body(intro)
        body(features)

    # ── 6. Cloud Architecture ──
    h1("6. Proposed Cloud Architecture")
    h2("6.1 How a Request Flows Through the System")
    body(
        "A user opens https://project-lifelink-1.vercel.app. Vercel serves the React "
        "app from its nearest edge location. The app then calls the backend API at "
        "https://lifelink-backend-tunc.onrender.com over HTTPS, sending a JWT token "
        "with every request."
    )
    body(
        "The FastAPI backend on Render checks the token and the user's role, then "
        "uses Supabase PostgreSQL for structured data and Supabase Storage for "
        "files. When a document is uploaded, the file is saved and the API responds "
        "straight away; text extraction and the Groq AI call run in the background "
        "and the document status changes from pending to completed."
    )
    body(
        "For deployment, a push to GitHub triggers GitHub Actions checks, and Vercel "
        "and Render rebuild and redeploy their parts automatically. The full diagram "
        "is shown in Fig. 1 (Section 9.2)."
    )
    h2("6.2 Layered View")
    table(
        [
            ["Layer", "Service", "Responsibility"],
            ["Presentation", "Vercel", "React SPA, CDN, HTTPS"],
            [
                "Application",
                "Render (FastAPI in Docker)",
                "REST API, auth, ML risk models, AI orchestration, scheduler",
            ],
            ["Data", "Supabase PostgreSQL + pgvector", "Structured data, embeddings"],
            ["Storage", "Supabase Storage", "Uploaded medical documents"],
            ["AI", "Groq Cloud API", "LLM extraction and assistant replies"],
            ["DevOps", "GitHub + GitHub Actions", "Version control, CI, deploy"],
        ]
    )

    # ── 7. Security ──
    h1("7. Security Considerations")
    h2("7.1 Authentication & Authorization")
    table(
        [
            ["Mechanism", "Implementation"],
            [
                "JWT tokens",
                "Short-lived access token and longer-lived refresh token, signed with "
                "a secret generated by Render",
            ],
            ["Password hashing", "bcrypt with 12 rounds"],
            [
                "Role-based access",
                "patient, doctor and admin roles enforced by a require_role() "
                "dependency on protected endpoints",
            ],
            [
                "Data isolation",
                "Every query is filtered by the logged-in user's ID, so patients see "
                "only their own records",
            ],
        ]
    )
    h2("7.2 Encryption")
    table(
        [
            ["Layer", "Mechanism"],
            ["Browser ↔ Vercel / Render", "HTTPS (TLS) with certificates managed by the platforms"],
            ["Backend ↔ Supabase", "TLS-encrypted database and storage connections"],
            ["Data at rest", "Supabase encrypts database and storage disks"],
            [
                "Files",
                "Private bucket; downloads only through expiring pre-signed URLs",
            ],
        ]
    )
    h2("7.3 Secrets, Network & Backups")
    body(
        "API keys, the database URL, storage keys and SMTP credentials are kept as "
        "environment variables in the Render dashboard and in a local .env file "
        "that is excluded from Git. CORS only allows the Vercel frontend origin. "
        "File uploads are limited to PDF and image types up to 50 MB."
    )
    body(
        "The database schema is versioned with Alembic migrations, so it can be "
        "recreated on any PostgreSQL server. The free Supabase tier has limited "
        "backup options; a paid plan adds daily backups and point-in-time recovery, "
        "which would be required before storing real patient data."
    )

    # ── 8. SDG Alignment ──
    h1("8. Alignment with UN Sustainable Development Goals")
    body(
        "LIFELINK is a healthcare product, so its main contribution is to SDG 3 "
        "(Good Health and Well-being). Because it is delivered entirely over the "
        "cloud, it also supports SDG 9 (Industry, Innovation and Infrastructure). "
        "The specific targets it addresses are listed below."
    )
    h2("8.1 SDGs and Targets Supported")
    table(
        [
            ["SDG / Target", "Target (summary)", "How LIFELINK Contributes"],
            [
                "SDG 3 — Target 3.4",
                "Reduce premature deaths from non-communicable diseases by one third "
                "through prevention and treatment.",
                "ML models flag risk of cardiovascular disease, diabetes and chronic "
                "kidney disease early, with the factors behind each score and "
                "lifestyle recommendations. Medicine and follow-up reminders support "
                "adherence.",
            ],
            [
                "SDG 3 — Target 3.8",
                "Achieve universal health coverage, including access to quality "
                "essential health services.",
                "Any patient with a browser can store and carry a complete medical "
                "history for free, so a new doctor or emergency team sees the full "
                "picture.",
            ],
            [
                "SDG 3 — Target 3.d",
                "Strengthen capacity for early warning, risk reduction and "
                "management of health risks.",
                "Abnormal lab values, a health score and risk levels are surfaced on "
                "the dashboard automatically after each upload.",
            ],
            [
                "SDG 9 — Target 9.c",
                "Significantly increase access to information and communications "
                "technology.",
                "AI document reading, an AI health assistant and risk prediction are "
                "offered as a web service that needs no installation or special "
                "hardware.",
            ],
        ]
    )
    h2("8.2 How the Project Contributes")
    bullet(
        " Scattered paper and PDF records become one searchable, chronological "
        "timeline, so medical history is not lost between hospitals.",
        "Unified records:",
    )
    bullet(
        " OCR and an LLM pull out medications, diagnoses and lab values, so "
        "patients can understand their own reports.",
        "Health literacy:",
    )
    bullet(
        " Risk scores for three common chronic diseases encourage patients to "
        "seek care before complications appear.",
        "Prevention:",
    )
    bullet(
        " Family profiles let one person manage records for elderly parents or "
        "children.",
        "Family care:",
    )
    h2("8.3 Expected Impact")
    table(
        [
            ["Dimension", "Expected Impact"],
            [
                "Social",
                "Better continuity of care, fewer medication conflicts, and earlier "
                "detection of chronic disease. Patients and caregivers gain control "
                "over their own health data.",
            ],
            [
                "Economic",
                "Fewer repeated diagnostic tests because previous reports are always "
                "available. Early risk detection can avoid costlier late-stage "
                "treatment. The platform runs at zero hosting cost on free cloud "
                "tiers, so it can be offered free to users.",
            ],
            [
                "Environmental",
                "Digital records replace printed reports and repeat tests, reducing "
                "paper and lab consumables. Shared, multi-tenant cloud platforms use "
                "hardware more efficiently than a dedicated server per clinic.",
            ],
        ]
    )

    # ── 9. Cloud Services Used ──
    h1("9. Cloud Services Used")
    body(
        "LIFELINK is live on the internet. Frontend: "
        "https://project-lifelink-1.vercel.app — Backend API: "
        "https://lifelink-backend-tunc.onrender.com."
    )
    h2("9.1 Services in the Live Deployment")
    table(
        [
            ["#", "Cloud Service", "Model", "Used For"],
            [
                "1",
                "Vercel",
                "PaaS + CDN",
                "Hosts the React frontend on a global edge network with automatic "
                "HTTPS; rebuilds on every push to GitHub.",
            ],
            [
                "2",
                "Render Web Service",
                "PaaS",
                "Runs the FastAPI backend as a Docker container (Singapore region), "
                "with a health check on /api/v1/health and auto-deploy from GitHub.",
            ],
            [
                "3",
                "Supabase PostgreSQL",
                "DBaaS",
                "Managed PostgreSQL 17 with pgvector; stores users, records, "
                "timeline, risk assessments, reminders and family profiles.",
            ],
            [
                "4",
                "Supabase Storage",
                "Object storage",
                "Private S3-compatible bucket (lifelink-documents) for uploaded "
                "reports, accessed with pre-signed download URLs.",
            ],
            [
                "5",
                "Groq Cloud API",
                "AI API (SaaS)",
                "LLM inference (Qwen) for document extraction, summaries and the AI "
                "health assistant.",
            ],
            [
                "6",
                "GitHub + GitHub Actions",
                "DevOps SaaS",
                "Source control and CI pipeline; pushes to main trigger "
                "redeployment.",
            ],
            [
                "7",
                "Gmail SMTP",
                "SaaS",
                "Sends reminder emails from the background scheduler.",
            ],
        ]
    )
    h2("9.2 Architecture Diagram")
    els.append(image_par())
    h2("9.3 Benefits of Using the Cloud")
    table(
        [
            ["Benefit", "How LIFELINK Gets It"],
            [
                "Scalability",
                "Vercel's CDN serves any number of frontend users. The backend is a "
                "stateless container, so Render can run more or larger instances on "
                "a paid plan without code changes. Supabase database and storage "
                "grow with usage.",
            ],
            [
                "Cost",
                "No hardware to buy. The current deployment costs $0 per month on "
                "free tiers; paid tiers are only needed when traffic grows.",
            ],
            [
                "Availability",
                "The providers handle uptime and patching. Render restarts the "
                "container if the health check fails. Note: the free Render tier "
                "sleeps after 15 minutes idle, so the first request takes up to a "
                "minute.",
            ],
            [
                "Security",
                "HTTPS everywhere, JWT authentication with role-based access, bcrypt "
                "password hashing, a private storage bucket with expiring pre-signed "
                "URLs, and secrets kept in environment variables instead of code.",
            ],
            [
                "Accessibility",
                "Patients and doctors use it from any device with a browser, "
                "anywhere, with no installation. Records are available during "
                "emergencies or when changing doctors.",
            ],
        ]
    )

    # ── 10. Conclusion ──
    h1("10. Conclusion")
    body(
        "This report worked backward from what LIFELINK needs to do: authenticate "
        "users, store medical documents, read them with AI, build a health "
        "timeline and predict chronic disease risk. Each need was mapped to a "
        "managed cloud service."
    )
    body(
        "Vercel, Render and Supabase were chosen because they fit the existing "
        "code (Docker backend, S3-compatible storage client, PostgreSQL with "
        "pgvector), deploy automatically from GitHub, and cost nothing on their "
        "free tiers. Groq provides the language model, and GitHub Actions checks "
        "every change."
    )
    body(
        "The project is live, which shows the design works in practice. Security "
        "is handled through HTTPS, JWT with role-based access, bcrypt, a private "
        "storage bucket and secrets kept out of the code. Moving to paid tiers "
        "would remove the cold-start delay and add database backups."
    )
    body(
        "LIFELINK directly supports UN SDG 3 by helping patients detect chronic "
        "disease risk early and keep their medical history in one accessible place."
    )

    # ── 11. References ──
    h1("11. References")
    for r in [
        '[1] P. Mell and T. Grance, "The NIST Definition of Cloud Computing," NIST '
        "Special Publication 800-145, Sep. 2011. Available: "
        "https://csrc.nist.gov/publications/detail/sp/800-145/final",
        '[2] Vercel, "Vercel Documentation." Available: https://vercel.com/docs',
        '[3] Render, "Render Documentation — Web Services and Blueprints." '
        "Available: https://render.com/docs",
        '[4] Supabase, "Supabase Documentation — Database and Storage." Available: '
        "https://supabase.com/docs",
        '[5] pgvector, "Open-source vector similarity search for Postgres." '
        "Available: https://github.com/pgvector/pgvector",
        '[6] Groq, "GroqCloud Documentation." Available: https://console.groq.com/docs',
        '[7] S. Ramírez, "FastAPI — Modern Web Framework for Building APIs with '
        'Python." Available: https://fastapi.tiangolo.com/',
        '[8] United Nations, "Goal 3: Ensure healthy lives and promote well-being '
        'for all at all ages," UN DESA. Available: https://sdgs.un.org/goals/goal3',
        '[9] United Nations, "Goal 9: Industry, Innovation and Infrastructure," UN '
        "DESA. Available: https://sdgs.un.org/goals/goal9",
    ]:
        els.append(clone(REF, r))
    return els


# ─── Assemble ────────────────────────────────────────────────────────────
def main():
    draw_diagram()
    body_el = d.element.body

    # Drop everything from the old Section 3 heading to the end (keep sectPr).
    start = P[40]._p
    removing = False
    for el in list(body_el):
        if el is start:
            removing = True
        if removing and el.tag != qn("w:sectPr"):
            body_el.remove(el)

    sect = body_el.find(qn("w:sectPr"))
    for el in build_sections():
        sect.addprevious(el)

    # Table of contents (paragraphs 14-20 = old items 3-9)
    toc = [
        "3.  Identification of Suitable Cloud Services",
        "4.  Selection and Justification of Cloud Service Provider",
        "5.  Description of Selected Cloud Services and Features",
        "6.  Proposed Cloud Architecture",
        "7.  Security Considerations",
        "8.  Alignment with UN Sustainable Development Goals",
        "9.  Cloud Services Used",
    ]
    for i, t in enumerate(toc):
        set_text(P[14 + i]._p, t)
    last = P[20]._p
    for t in reversed(["10.  Conclusion", "11.  References"]):
        last.addnext(clone(TOC_ITEM, t))

    # Cover page
    P[6]._p.addprevious(clone(P[6], "Team No: ____"))
    set_text(P[9]._p, "Submission Date: October 2026")

    # Section 1-2 fixes (old text referred to AWS / GPT-4o-mini / XGBoost)
    set_text(
        P[32]._p,
        "Deploy the whole system on managed cloud platforms (Vercel, Render, "
        "Supabase) so it stays available, secure, and able to grow with demand.",
    )
    func = d.tables[1]
    for row in func.rows:
        if row.cells[0].text.startswith("AI Document Processing"):
            set_cell(
                row.cells[1],
                "Extracts text via PyMuPDF/OCR, then structures it using a Groq-"
                "hosted LLM (Qwen).",
            )
    core = d.tables[2]
    for row in core.rows:
        name = row.cells[0].text
        if name == "AI Processing":
            set_cell(row.cells[2], "Background task, outbound API access to the LLM")
        elif name == "Dashboard":
            set_cell(row.cells[2], "Fast aggregation queries on a managed database")
        elif name == "Risk Assessment":
            set_cell(
                row.cells[1],
                "Gradient Boosting inference, per-feature explanation, score storage",
            )
            set_cell(
                row.cells[2], "Compute with ML libraries; model files in container"
            )
    nfr = {
        "Scalability": "Stateless containers that can be scaled on the host, CDN "
        "for the frontend",
        "Availability": "Managed hosting with health checks and automatic restart",
        "Performance": "CDN for static files and an indexed managed database",
        "Security": "Encryption in transit and at rest, private storage, secrets in "
        "environment variables",
        "Cost efficiency": "Free tiers now; pay-as-you-go plans when usage grows",
    }
    for row in d.tables[3].rows:
        for k, v in nfr.items():
            if row.cells[0].text.startswith(k):
                set_cell(row.cells[1], v)

    d.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()

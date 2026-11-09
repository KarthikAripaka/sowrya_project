# Evidence-Based Medical Report and Chest X-ray Interpretation System

An enterprise-grade, cloud-native healthcare AI application that interprets medical documents and chest radiographs using **Groq Cloud API**, **Cloud Document OCR**, **Retrieval-Augmented Generation (RAG)** with **PostgreSQL pgvector**, and a **Hosted Medical Imaging API**.

> **MANDATORY MEDICAL SAFETY DISCLAIMER**  
> This application provides AI-assisted educational explanations of medical reports and diagnostic images. It does **NOT** provide a medical diagnosis or replace consultation with a qualified healthcare professional. AI-generated results may contain errors and must be reviewed by an appropriately qualified medical professional. Never alter prescribed medical treatments without professional medical supervision.

---

## 1. Key Highlights & Cloud AI Architecture

- **100% Cloud-Native AI Stack**: Completely eliminates local GPUs, local model weights, and heavy local inference dependencies. Powered by Groq's low-latency cloud inference.
- **Primary LLM: Groq Cloud API**: Integrates official Groq SDK and endpoints using `llama-3.3-70b-versatile` (default) and `llama-3.1-8b-instant` with structured JSON mode.
- **Strict API Key Security**: `GROQ_API_KEY` is stored **strictly in backend environment variables**. It is never exposed in client-side code or bundled in frontend bundles.
- **Reusable `LLMProvider` Abstraction**: Clean provider interface (`LLMProvider`) with `GroqProvider` as the default. Switch cloud providers via `LLM_PROVIDER` in `.env` without modifying business logic.
- **Strict Medical Safety & Transparency**:
  - Distinguishes extracted factual findings from AI explanations.
  - Preserves exact numerical laboratory values and reference intervals without rounding or alteration.
  - **Never invents or fabricates X-ray findings**. If the hosted imaging API is unconfigured or unreachable, the system transparently indicates that imaging analysis is awaiting configuration rather than generating simulated disease scores.
- **Evidence-Grounded RAG**: Retrieves verified, peer-reviewed clinical guidelines exclusively from accredited medical institutions:
  - **MedlinePlus** (National Library of Medicine / NIH)
  - **PubMed** (National Center for Biotechnology Information)
  - **World Health Organization (WHO)**
  - **RadiologyInfo.org** (Radiological Society of North America / ACR)
- **Vector Database**: PostgreSQL with `pgvector` for clinical semantic search, with in-memory normalized semantic embeddings for zero-cost local development.
- **Cloud Document OCR**: Lossless digital PDF extraction via PyPDF (instant, zero cost), combined with Groq Vision (`llama-3.2-11b-vision-preview`) or OCR.space for scanned reports.
- **Automated Clinical PDF Export**: Generates professional PDF summaries using ReportLab with clinical reference intervals, doctor discussion points, and safety disclaimers.

---

## 2. Technology Stack

| Subsystem | Technology / Cloud Service | Role & Scope |
|---|---|---|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons, Recharts | Linear/Stripe-inspired healthcare SaaS UI across 8 responsive pages |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 | Asynchronous REST API with JWT security and centralized error handling |
| **Primary Cloud LLM** | **Groq Cloud API** (`llama-3.3-70b-versatile`) | Fast, structured clinical synthesis, doctor discussion points, and plain-language explanations |
| **LLM Interface** | `LLMProvider` / `GroqProvider` | Reusable provider abstraction with rate-limit (429), timeout, and 401 error handling |
| **Document OCR** | PyPDF + Groq Vision / OCR.space | Exact numerical value preservation from digital PDFs and cloud OCR for scanned documents |
| **Biomedical NER** | Medical NLP Engine | Deterministic parser for laboratory tests, values, units, reference intervals, and flags |
| **Vision Inference** | **Hosted Medical Imaging API** | Cloud-inference adapter for chest radiograph evaluation across 14 thoracic pathologies |
| **Vector Storage** | **PostgreSQL + pgvector** | Vector index for peer-reviewed medical guideline retrieval |
| **Cache** | Redis (with in-memory fallback) | Rate limiting, session caching, and performance optimization |
| **File Storage** | Local Storage / S3 / Cloudflare R2 | Uploaded medical report storage with user-level isolation |
| **PDF Generation** | ReportLab | Automated clinical report and X-ray interpretation PDF export |
| **Deployment** | Docker, Docker Compose, GitHub Actions | Production multi-container orchestration |

---

## 3. Complete Directory Structure

```text
medical-ai-assistant/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── analysis/[id]/page.tsx   # Page 5: Report Analysis & Citations
│   │   │   ├── dashboard/page.tsx       # Page 3: User Dashboard & Telemetry
│   │   │   ├── history/page.tsx         # Page 7: Analysis History & PDF Downloads
│   │   │   ├── login/page.tsx           # Page 2: Secure Login & Registration
│   │   │   ├── settings/page.tsx        # Page 8: Cloud AI Provider Settings & DPDP Deletion
│   │   │   ├── upload/page.tsx          # Page 4: Document Upload & Multi-Stage Stepper
│   │   │   ├── xray/[id]/page.tsx       # Page 6: Saved X-ray Study & Quality Metrics
│   │   │   ├── xray/page.tsx            # Page 6: Chest Radiograph Analyzer
│   │   │   ├── globals.css              # Custom healthcare styles & scrollbars
│   │   │   ├── layout.tsx               # Root layout with banner & navigation
│   │   │   └── page.tsx                 # Page 1: Healthcare SaaS Landing Page
│   │   ├── components/
│   │   │   └── common/
│   │   │       ├── DisclaimerBanner.tsx # Medical safety disclaimer banner
│   │   │       ├── Footer.tsx           # Accreditation, knowledge sources & compliance
│   │   │       └── Navbar.tsx           # Navigation bar with live auth status
│   │   └── lib/
│   │       └── api.ts                   # Type-safe API client & JWT token manager
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── next.config.js
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── embeddings/              # CloudEmbeddingProvider (deterministic semantic vectorizer)
│   │   │   ├── llm/                     # LLMProvider interface & GroqProvider (Groq SDK client)
│   │   │   ├── nlp/                     # MedicalNLPEngine (biomarker & reference interval parser)
│   │   │   ├── ocr/                     # CloudOCREngine (PyPDF + Groq Vision / OCR.space)
│   │   │   ├── rag/                     # MedicalRAGPipeline (MedlinePlus/PubMed/WHO retrieval)
│   │   │   └── vision/                  # XrayVisionEngine (Hosted medical imaging client)
│   │   ├── api/
│   │   │   ├── v1/endpoints/            # Auth, Reports, OCR, Analysis, RAG, History, Users, Dashboard
│   │   │   ├── deps.py                  # JWT dependency & demo user injection
│   │   │   └── api.py                   # Central API routing
│   │   ├── core/                        # Security (PBKDF2/JWT) & Configuration Settings
│   │   ├── database/                    # SQLAlchemy engine & session maker
│   │   ├── models/                      # 11 Relational database models
│   │   ├── schemas/                     # Pydantic v2 validation schemas
│   │   ├── services/                    # ReportLab clinical PDF summary generator
│   │   └── main.py                      # FastAPI application entrypoint
│   ├── tests/
│   │   ├── test_backend_core.py         # Unit tests (Groq, Rate limits, Safety, NLP, RAG, Security)
│   │   └── test_api_direct.py           # Integration tests for all REST endpoints & database
│   └── requirements.txt                 # Clean cloud dependencies (groq, pgvector, boto3, etc.)
│
├── knowledge_base/
│   └── curated/                         # Curated MedlinePlus, PubMed, WHO, RadiologyInfo documents
├── storage/
│   ├── uploads/                         # User-isolated document storage
│   └── reports/                         # Generated summary PDFs
├── docker/
│   ├── backend.Dockerfile               # Multi-stage Python 3.11 backend container
│   └── frontend.Dockerfile              # Next.js 14 Alpine production container
├── docker-compose.yml                   # Production orchestration (Backend, Frontend, pgvector, Redis)
├── .env.example                         # Environment configuration template
├── .env                                 # Local environment variables
└── README.md
```

---

## 4. Groq API Configuration & Setup

### Free Tier Setup Guide
1. Create a free account at [Groq Console](https://console.groq.com).
2. Navigate to **API Keys** and generate a new key (`gsk_...`).
3. Add your key to the backend `.env` file:
   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_your_actual_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   GROQ_TIMEOUT_SECONDS=30
   ```
4. **Free-Tier Limits & Usage**:
   - Groq provides generous free-tier requests per minute (RPM) and tokens per minute (TPM).
   - If the rate limit is exceeded, the backend returns an explicit HTTP 429 status code with clear guidance rather than crashing.
   - If `GROQ_API_KEY` is not configured, the system gracefully runs in verified fallback mode using curated medical knowledge bases and informs the user via the Dashboard and Settings page.

---

## 5. Automated Test Verification

All automated tests execute with **100% success**:

```bash
# 1. Backend Core Unit Tests (Groq, Auth, NLP, RAG, Safety, OCR)
.\.venv\Scripts\python.exe -u backend/tests/test_backend_core.py
```
**Output:**
```text
Running comprehensive core test suite...
✓ Security password hashing verified.
✓ JWT token creation & decoding verified.
✓ Medical NLP & entity preservation verified.
✓ RAG medical evidence retrieval verified.
✓ GroqProvider initialization verified.
✓ GroqProvider missing key handling verified.
✓ GroqProvider invalid key error handling verified.
✓ GroqProvider rate limit (HTTP 429) handling verified.
✓ Missing imaging API safety verified (never invents fake findings).
✓ Cloud OCR file validation verified.
ALL 10 CORE AI & SECURITY TESTS PASSED WITH 100% SUCCESS!
```

```bash
# 2. Direct API & Database Operations Integration Tests
.\.venv\Scripts\python.exe -u backend/tests/test_api_direct.py
```
**Output:**
```text
Beginning Comprehensive Direct API & Database Verification...
✓ Root and Health Check verified.
✓ Registration verified: Dr. Jane Smith (test.physician@medicalai.org)
✓ Authentication & JWT generation verified.
✓ RAG Knowledge Base verified with 14 peer-reviewed documents.
✓ Dashboard stats & Cloud AI telemetry verified.
✓ Unified history retrieval verified.
✓ DPDP/GDPR User Data Deletion verified.
ALL BACKEND API MODULES & DATABASE OPERATIONS VERIFIED WITH 100% SUCCESS!
```

```bash
# 3. Frontend TypeScript Compilation
npx --prefix frontend tsc --noEmit -p frontend/tsconfig.json
# (0 errors - clean compilation)
```

---

## 6. Installation & Launch Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Free [Groq API Key](https://console.groq.com)

### Step 1: Backend Setup
```bash
# 1. Navigate to project root and activate virtual environment
.venv\Scripts\activate   # On Windows
# source .venv/bin/activate  # On Linux/macOS

# 2. Install cloud dependencies
pip install -r backend/requirements.txt
pip install email-validator greenlet

# 3. Configure .env file
cp .env.example .env
# Edit .env and set your GROQ_API_KEY

# 4. Start FastAPI server
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Endpoint: `http://localhost:8000`
- Swagger Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`

### Step 2: Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:3000`
- Default Demo User: `demo@medicalai.org` / `MedicalAI2026!` (or register a new account on `/login`)

---

## 7. Docker Deployment Instructions

To spin up the complete cloud-ready container stack (Backend, Next.js Frontend, PostgreSQL with pgvector, and Redis):

```bash
# 1. Provide your GROQ_API_KEY in .env
export GROQ_API_KEY=gsk_your_key_here

# 2. Build and start containers
docker compose up -d --build

# 3. Verify services
docker compose ps
```

Service Access Points:
- Web Application: `http://localhost:3000`
- REST API Documentation: `http://localhost:8000/docs`
- PostgreSQL with pgvector: `localhost:5432`
- Redis: `localhost:6379`

---

## 8. Medical Safety & Ethical Boundaries

1. **Educational & Research Purpose**: This system is designed for patient health literacy, educational review, and clinical workflow assistance. It is **not FDA or CE cleared as Medical Device Software (SaMD)**.
2. **Strict Non-Fabrication Rule**: The system never invents laboratory values, disease labels, or radiograph findings. If external vision or cloud services are unconfigured or unavailable, it transparently indicates service unavailability.
3. **Mandatory Physician Review**: All radiographic features and laboratory out-of-range markers must be clinically correlated by licensed healthcare professionals.

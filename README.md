# AI-Powered Customer Feedback Intelligence & Sentiment Analytics Platform

An enterprise-grade, production-ready, end-to-end customer feedback intelligence platform that combines customer survey responses, online reviews, and customer support messages to uncover recurring themes, classify sentiment, detect shifts over time, flag data quality anomalies, prioritize service improvements, and track action items with full auditability.

---

## 1. Project Overview

Organizations receive thousands of customer signals across multiple channels, but these are often fragmented and difficult to act upon. This platform unifies disparate feedback sources into a single analytical pipeline:

- **Master & Transactional Foundations**: 18 relational entities managing customers, products, channels, surveys, tickets, reviews, and action items.
- **Deterministic Synthetic Generation Engine**: Generates realistic, balanced, privacy-safe multilingual feedback using a fixed random seed (`20261022`) in both **Starter** and **Full** execution modes.
- **NLP Sentiment Engine**: Multi-class sentiment classification (`POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED`) with confidence scoring, explainability tokens, and decision routing rules.
- **Multi-Label Theme Identification**: Classifies feedback across an 18-theme taxonomy using a hybrid keyword and TF-IDF cosine similarity engine with unknown-theme anomaly detection.
- **Time-Series Sentiment Shift Detection**: Flags sudden surges in negative sentiment (e.g. $\ge 20\%$ spike) across specific products and channels, storing them as discrete alerts.
- **Service Improvement Priority Engine**: Computes normalized 0–100 priority scores using a 5-factor weighted model to recommend targeted business interventions.
- **Action Item Management**: Full lifecycle state machine (`OPEN` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED` $\rightarrow$ `CLOSED` with `BLOCKED` exceptions) with immutable audit history.
- **Data Quality & Exception Management**: Automatically detects 10 negative data quality scenarios including PII leaks, sentiment contradictions, duplicate submissions, and taxonomy violations.
- **Interactive React Dashboard**: Modern, responsive dark-themed dashboard built with React 19, TypeScript, Tailwind CSS v4, Lucide icons, and Recharts.

---

## 2. Platform Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React 19 + TypeScript UI                        │
│   Overview | Feedback Explorer | Sentiment | Themes | Trends | Actions │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API
┌───────────────────────────────────▼────────────────────────────────────┐
│                         FastAPI Backend Service                        │
│   Master Data | Analytics | NLP Inference | Actions | Data Quality     │
├───────────────────────────────────┬────────────────────────────────────┤
│           AI / ML Engines         │       Data Quality & Audit         │
│   • TF-IDF Logistic Regression    │   • 10 Automated Integrity Rules   │
│   • Multi-Label Theme Extractor   │   • PII Masking (SSN, Phone)       │
│   • Shift & Anomaly Detector      │   • Immutable State Audit Trail    │
│   • 5-Factor Priority Scoring     │   • Isolated Ground Truth Splits   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQLAlchemy ORM
┌───────────────────────────────────▼────────────────────────────────────┐
│                    Relational Database (SQLite / Postgres)             │
│   18 Core Entities + Bridge Tables + Performance Indices + Audits      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

- **Frontend**: React 19, TypeScript, Tailwind CSS v4, Recharts, Lucide React, Vite 8.
- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn.
- **AI/ML & NLP**: Scikit-learn, Pandas, NumPy, TF-IDF n-gram vectorization, Logistic Regression with probability calibration.
- **Database**: SQLite (local single-command execution) / PostgreSQL (enterprise container deployment).
- **Testing**: Pytest with automated unit, integration, and data quality suites.
- **Containerization**: Docker, Docker Compose.

---

## 4. Prerequisites

- **Python**: $\ge 3.10$ (tested on Python 3.13)
- **Node.js**: $\ge 18$ (tested on Node v24)
- **Package Managers**: `pip`, `npm` or `pnpm`
- **Docker & Docker Compose** (optional for containerized deployment)

---

## 5. Quickstart & Installation Instructions

### Step 1: Clone or Navigate to Project Directory
```powershell
cd d:\yotta
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default configuration:
```ini
DATABASE_URL=sqlite:///./customer_feedback.db
API_PORT=8000
API_HOST=0.0.0.0
RANDOM_SEED=20261022
APP_ENV=development
```

### Step 3: Install Backend Dependencies
```powershell
pip install -r backend/requirements.txt
```

### Step 4: Install Frontend Dependencies & Build
```powershell
pnpm --dir frontend install
cd frontend; npx vite build; cd ..
```

---

## 6. CLI Execution Scripts

The platform includes automated scripts in `scripts/`:

### 1. Deterministic Data Generation
Generates synthetic master data, dependent transactions, injected anomalies, and exports ground truth.
```powershell
# Starter mode (1,000 customers, 12,010 total records)
python scripts/generate_data.py --mode starter

# Full enterprise mode (10,000 customers, 120,100 records)
python scripts/generate_data.py --mode full
```

### 2. Automated Data Quality Audit
Runs all 10 integrity validation checks and outputs the pass rate report:
```powershell
python scripts/validate_data.py
```

### 3. Model Training
Trains the sentiment classifier strictly on the `TRAIN` ground truth split (preventing label leakage):
```powershell
python scripts/train_models.py
```

### 4. Model Evaluation & Benchmarks
Calculates accuracy, precision, recall, macro F1, micro F1, Hamming loss, and confusion matrix on the holdout `TEST` split:
```powershell
python scripts/evaluate_models.py
```

### 5. Reproducibility Verification
Verifies bitwise deterministic reproducibility under fixed seed `20261022`:
```powershell
python scripts/verify_reproducibility.py
```

### 6. Batch Feedback Processing
Executes batch inference over raw customer feedback records:
```powershell
python scripts/process_feedback.py --batch-size 2000
```

---

## 7. Running the Application

### Running the Backend API
Start the FastAPI server:
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health Check: `http://localhost:8000/api/health`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Unified App Dashboard: `http://localhost:8000/` (serves the pre-built frontend)

### Running Frontend in Development Mode
To run Vite with hot-module replacement:
```powershell
cd frontend
npx vite
```
Open `http://localhost:5173/` in your browser. All API requests are automatically proxied to `http://localhost:8000`.

---

## 8. Docker & Container Deployment

### Running with Docker Compose
```powershell
docker-compose up --build
```
This builds the multi-stage image (compiling frontend assets and setting up the Python runtime) and exposes the platform at `http://localhost:8000`.

---

## 9. Running Automated Tests

Run the full pytest suite:
```powershell
pytest
```
Covers:
- Primary key and foreign key integrity.
- Lifecycle state transitions and invalid state exceptions.
- NLP preprocessor PII masking and test-label leakage detection.
- Sentiment and theme classification.
- Full FastAPI endpoint integration.
- Deterministic seed reproducibility.

---

## 10. System Documentation Links

- [Data Dictionary](file:///d:/yotta/docs/DATA_DICTIONARY.md): Complete field definitions for all 18 entities.
- [Database Schema](file:///d:/yotta/docs/DATABASE_SCHEMA.md): Mermaid ER diagram, cascade actions, and indexing.
- [API Documentation](file:///d:/yotta/docs/API_DOCUMENTATION.md): REST API endpoints and payloads.
- [Model Documentation](file:///d:/yotta/docs/MODEL_DOCUMENTATION.md): Machine learning architecture and benchmarks.
- [Data Generation Guide](file:///d:/yotta/docs/DATA_GENERATION.md): Deterministic generator protocols.
- [Validation Report](file:///d:/yotta/docs/VALIDATION_REPORT.md): Automated data quality scan findings.
- [Reproducibility Report](file:///d:/yotta/docs/REPRODUCIBILITY_REPORT.md): SHA-256 bitwise hash match verification.
- [Source Code Manifest](file:///d:/yotta/docs/SOURCE_MANIFEST.md): Complete codebase directory layout.

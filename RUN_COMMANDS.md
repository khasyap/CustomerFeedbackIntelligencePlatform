# RUN COMMANDS GUIDE
## Customer Feedback Intelligence & Sentiment Analytics Platform

This guide provides all copy-pasteable commands to run the platform, development servers, background AI pipelines, data generators, and tests.

---

## 1. Quick Start: The Recommended Single Command (Production Mode)

Starts the unified FastAPI backend which serves **both** the REST API at `/api` and the compiled React 19 dashboard at `/` on port **8000**:

```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

* **Interactive Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)
* **Interactive OpenAPI/Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **API Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

> **Tunneling with ngrok**: If using ngrok, simply tunnel port 8000:
> ```powershell
> ngrok http 8000
> ```

---

## 2. Development Mode (Dual Process with Hot Reload)

If you are developing frontend components with live hot-reloading (Vite HMR), run **both** processes in separate terminals:

### Terminal 1: Backend API Server
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Vite Frontend Dev Server
```powershell
cd frontend
npx vite
```
* **Dev Server URL**: [http://localhost:5173/](http://localhost:5173/)
* **ngrok Tunnel**: [https://overbill-target-rectangle.ngrok-free.dev](https://overbill-target-rectangle.ngrok-free.dev)
*(Note: Terminal 1 must be running for Terminal 2 to proxy `/api` calls).*

---

## 3. Automated Test Suite

Run the full automated test suite (16 tests covering data integrity, state transitions, API endpoints, and NLP models):

```powershell
pytest
```

For detailed per-test execution output:
```powershell
pytest -v
```

---

## 4. Synthetic Data Generation Engine (Seed `20261022`)

```powershell
# 1. Generate Starter Mode (1,000 customers, 12,010 total feedback records)
python scripts/generate_data.py --mode starter

# 2. Generate Full Enterprise Mode (10,000 customers, 120,100 total feedback records)
python scripts/generate_data.py --mode full

# 3. Reset existing database and regenerate fresh dataset
python scripts/generate_data.py --mode starter --reset-db
```

---

## 5. Automated Data Quality Audit (10 Rules)

Scans the database across 10 data quality and business logic constraints:

```powershell
python scripts/validate_data.py
```

---

## 6. AI Model Training & Evaluation

```powershell
# Train the sentiment classifier strictly on the TRAIN ground-truth partition
python scripts/train_models.py

# Benchmark sentiment and multi-label theme models on the holdout TEST partition
python scripts/evaluate_models.py
```

---

## 7. Batch NLP Inference Pipeline

Classifies unanalyzed raw reviews, survey responses, and support messages:

```powershell
python scripts/process_feedback.py --batch-size 2000
```

---

## 8. Deterministic Seed Reproducibility Verification

Verifies 100% bitwise SHA-256 hash matching across dual generator runs under seed `20261022`:

```powershell
python scripts/verify_reproducibility.py
```

---

## 9. Rebuild Frontend Static Bundle

Compiles TypeScript, Tailwind CSS, and React assets into `frontend/dist/`:

```powershell
cd frontend
npx vite build
cd ..
```

---

## 10. Containerized Deployment (Docker)

```powershell
docker-compose up --build
```
* Accessible at [http://localhost:8000/](http://localhost:8000/).


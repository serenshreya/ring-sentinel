# Ring Sentinel 🛡️
### Merchant Fraud-Ring Detector & Risk Advisory System
**Razorpay AI Buildathon — Track: AI Risk Manager**

---

## 📌 Executive Summary

Merchants lose millions to coordinated return and refund abuse when malicious syndicates register multiple distinct customer accounts to evade velocity limits. Traditional fraud filters evaluate transactions individually, failing to catch distributed abuse while mistakenly blocking legitimate high-value customers.

**Ring Sentinel** solves this with an **Identity Graph + Machine Learning + Fast LLM Explainability** pipeline:
1. **Identity Graph (NetworkX)**: Discovers connected customer accounts sharing hardware fingerprints (`device_id`), network fingerprints (`ip_address`), financial beneficiaries (`refund_bank_account`), or physical destinations (`delivery_address`).
2. **Behavioral ML Risk Scorer (Scikit-Learn)**: Analyzes multi-signal cluster density, refund velocity, and transaction deviation to output calibrated risk scores (0.0% to 100.0%) that clearly separate organized fraud rings from innocent address sharing (e.g., student hostels or apartment complexes).
3. **Plain-English Explainability (Groq / Qwen 3.8-27B)**: Synthesizes graph signals into concise, non-technical explanations for human risk analysts in milliseconds.

> [!IMPORTANT]
> **Advisory-Only Defense Guardrail**: Ring Sentinel is strictly an advisory intelligence platform for human risk managers. It **NEVER** automatically moves money, freezes bank accounts, blocks payments, or takes irreversible financial actions. All outputs serve as defensible recommendations.

---
## 🔗 Live Demo

- **Live App:** https://ring-sentinel-ten.vercel.app
- **Backend API Docs (Swagger):** https://ring-sentinel.onrender.com/docs

> Note: The backend runs on a free-tier host and may take 30–60 seconds to wake up on the first request after inactivity.

---

## 🏗️ System Architecture

```
                                  +---------------------------------------+
                                  |     React 18 + Tailwind Dashboard     |
                                  |         http://localhost:5173         |
                                  +-------------------+-------------------+
                                                      |
                                          (Supabase JWT Bearer)
                                                      v
                                  +---------------------------------------+
                                  |        FastAPI Backend Engine         |
                                  |         http://localhost:8000         |
                                  +---------+-------------------+---------+
                                            |                   |
                        +-------------------+                   +-------------------+
                        |                                                           |
                        v                                                           v
        +-------------------------------+                           +-------------------------------+
        |    NetworkX Identity Graph    |                           |      Groq LLM Engine          |
        |  Nodes: Customer Accounts     |                           |  Model: qwen/qwen3.8-27b      |
        |  Edges: Device, IP, Bank,     |                           |  Task: 1-sentence explanation |
        |         Delivery Address      |                           |  Guardrails: No hallucinated  |
        +---------------+---------------+                           |              scores/actions   |
                        |                                           +-------------------------------+
                        v
        +-------------------------------+
        |   Scikit-Learn ML Scorer      |
        |  • Device Sharing Ratio       |
        |  • Bank Sharing Ratio         |
        |  • IP Sharing Ratio           |
        |  • Order Velocity & Deviation |
        +---------------+---------------+
                        |
                        v
        +-------------------------------+
        |       Supabase Cloud DB       |
        |  • public.orders (2,000 rows) |
        |  • public.clusters (14 rings) |
        |  • Row Level Security (RLS)   |
        +-------------------------------+
```

---

## 📊 Held-Out Test Set Performance

To prove real-world generalization and prevent data leakage:
- **Training Period (Days 0–24)**: Historical baseline containing Rings 1–4 and Student Residence Halls A–E.
- **Held-Out Test Period (Days 24–30)**: **100% novel, unseen fraud rings (Rings 5 & 6)** and unseen innocent hostels, strictly separated chronologically by timestamp (0% entity overlap).

```
====================================================================================================
METRIC                          RING SENTINEL (GRAPH + ML)       NAIVE BASELINE (> $500)
====================================================================================================
Precision                       100.0%                           33.3%
Recall                          100.0%                           10.2%
F1 Score                        1.00                             0.16
False Positive Rate (FPR)       0.0%                             2.9%
Legitimate Orders Disrupted     0 accounts                       10 innocent orders wrongly blocked
Missed Fraud Orders             0 orders                         44 fraud orders missed
====================================================================================================
```

### Why Ring Sentinel Outperforms Naive Rules:
- **Zero Legitimate Disruption**: The naive baseline flagged 10 innocent shoppers buying high-value items. Ring Sentinel recognized that student residence clusters have distinct devices and unique bank accounts, scoring them at **~8% risk** (0 false positives).
- **Catches Structured Low-Value Fraud**: Syndicates intentionally kept order amounts moderate ($200–$400). The naive rule missed **44 out of 49 fraud transactions** (10.2% recall). Ring Sentinel caught 100% of them by connecting device and refund bank reuse across accounts.

---

## 🎯 Continuous Risk Score Spectrum

```
====================================================================================================
CLUSTER ID   NATURE                       MEMBERS   ORDERS   FRAUD ORDERS   PREDICTED RISK SCORE
====================================================================================================
Cluster #3   Fraud Ring (Historical)      7         27       27             96.7% (High Risk)
Cluster #5   Fraud Ring (Historical)      7         27       27             96.7% (High Risk)
Cluster #1   Fraud Ring (Historical)      7         27       27             96.5% (High Risk)
Cluster #10  Novel Fraud Ring (Test Set)  7         26       26             95.3% (High Risk)
Cluster #4   Fraud Ring (Historical)      6         27       27             92.1% (High Risk)
Cluster #11  Novel Fraud Ring (Test Set)  5         26       26             83.7% (High Risk)
----------------------------------------------------------------------------------------------------
Cluster #9   Student Hostel G (Innocent)  5         5        0               9.7% (Low Risk)
Cluster #2   Student Hostel B (Innocent)  5         5        0               9.1% (Low Risk)
Cluster #7   Student Hostel E (Innocent)  5         5        0               8.6% (Low Risk)
Cluster #14  Student Hostel H (Innocent)  5         5        0               8.6% (Low Risk)
Cluster #6   Student Hostel D (Innocent)  5         5        0               8.4% (Low Risk)
Cluster #8   Student Hostel F (Innocent)  5         5        0               8.4% (Low Risk)
Cluster #13  Student Hostel C (Innocent)  5         5        0               8.2% (Low Risk)
Cluster #12  Student Hostel A (Innocent)  5         5        0               7.9% (Low Risk)
====================================================================================================
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone & Configure Environment
Create a `.env` file in the root directory (see `.env.example`):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
GROQ_API_KEY=your-groq-api-key
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate | On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. One-Click Launch (Windows)
Double-click [`run_all.bat`](run_all.bat) in the project root to start both backend and frontend servers simultaneously.

---

## 🔒 Security & Defense-Grade Design

- **Secret Zero-Exposure**: API keys and database credentials are read strictly from `.env` via `python-dotenv` and Vite environment variables. `.gitignore` strictly excludes all `.env` files, virtual environments, binaries, and build artifacts.
- **Row Level Security (RLS)**: Supabase tables (`orders`, `clusters`) enforce strict access control policies for authenticated users.
- **CORS Lock**: Backend CORS is explicitly restricted to `http://localhost:5173`.
- **Input Validation**: All incoming payloads and responses are validated via typed Pydantic models with constrained literals.
- **Rate Limiting**: SlowAPI limits API calls to 30 requests/minute per IP.
- **Anti-Hallucination Prompting**: The Groq LLM prompt enforces strict negative constraints preventing the model from deciding actions or fabricating risk scores.

---

## 👥 Verified Test Credentials

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Risk Analyst** | `analyst@ringsentinel.com` | `Test1234!` | Supabase JWT Authenticated |

# 🤖 OmniAI — Multi-Agent E-Commerce Automation Platform

> **An enterprise-grade, Multi-Agent AI system that automates product cataloging, dynamic market pricing, and RAG-powered customer support for digital storefronts.**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-EB5424?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Search-purple?style=for-the-badge)](https://www.trychroma.com/)

---

## 🌟 Live Demo & Visual Showcase

> *Below are real outputs captured from the live deployed platform, demonstrating the end-to-end journey from raw image ingestion to customer chat.*

### 1. Multi-Agent Pipeline & Dynamic Price Prediction
When a seller uploads a raw product photo, OmniAI orchestrates three specialized agents in real time:

<p align="center">
  <img src="docs/images/pipeline_output.png" alt="OmniAI Pipeline Output & Dynamic Pricing" width="900" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);" />
</p>

* **👁️ Vision Agent (Gemini 2.0 Flash Vision / Local CV Fallback):** Automatically analyzes visual characteristics, identifies materials (genuine silver), style category, and extracts dominant hex color swatches (`#ae6f6c`, `#5d322f`, `#935754`, `#e8e1e7`, `#c38d8b`).
* **✍️ Copywriter Agent (LLM Few-Shot JSON Enforcement):** Generates high-converting marketing assets—SEO product title (*"Modern Silver Jewelry piece - Handcrafted Excellence"*), a compelling 200-word listing, 12 targeted keyword tags, and key selling points.
* **💰 Pricing Agent (Trained XGBoost Regressor):** Ingests visual and market factors to forecast an optimal market price (**$232.21**) along with statistical confidence intervals (**$197.38 — $267.04**).

---

### 2. Context-Aware RAG Customer Support
Once cataloged, products are automatically embedded and indexed for instant semantic discovery by store shoppers:

<p align="center">
  <img src="docs/images/customer_chat_rag.png" alt="RAG-Powered Customer Support Chat" width="900" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);" />
</p>

* **🔍 Vector Search (ChromaDB):** Converts natural language customer queries into high-dimensional embeddings and computes cosine similarity against catalog items.
* **⚡ Relational Hydration (SQLite):** Hydrates exact pricing, inventory, and specs from the relational database.
* **💬 Grounded AI Responses:** The conversational agent delivers precise, hallucination-free recommendations with direct attribution cards and live pricing.

---

### 3. Glassmorphism Admin Portal & Live System Status
The administrative control plane provides real-time visibility into microservice health and pipeline states:

<p align="center">
  <img src="docs/images/admin_upload.png" alt="Admin Portal & System Status" width="900" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);" />
</p>

* **🔒 Authenticated Gateway:** Admin controls and batch ingest pipelines are locked behind token-based authorization (`X-Admin-Token`).
* **🟢 Real-Time Diagnostics:** Continuous health checks report backend API latency, database connection pools, and Gemini LLM availability.

---

## 🧠 System Architecture & Workflow

OmniAI follows a decoupled microservices design separating frontend presentation, API gateway orchestration, agent intelligence, and dual persistence.

```mermaid
flowchart TD
    subgraph Client ["Client Layer"]
        UI["Streamlit Frontend (ui/app.py)"]
        AdminView["Admin Dashboard"]
        CustomerView["Customer Chat View"]
        UI --> AdminView
        UI --> CustomerView
    end

    subgraph Gateway ["API & Security Gateway (FastAPI)"]
        API["FastAPI Orchestrator (api/main.py)"]
        Auth["verify_admin Guard (X-Admin-Token)"]
        API --> Auth
    end

    subgraph Agents ["Multi-Agent Execution Pipeline"]
        Vision["1. Vision Agent\n(Gemini 2.0 / KMeans + Edge CV)"]
        Copy["2. Copywriter Agent\n(Gemini 2.0 / Template Engine)"]
        Pricing["3. Pricing Agent\n(XGBoost Pipeline Pipeline)"]
        RAG["4. RAG Chat Agent\n(ChromaDB + Gemini 2.0)"]
    end

    subgraph Storage ["Dual Storage Layer"]
        SQLite[("SQLite Catalog DB\n(data/omniai.db)")]
        Chroma[("ChromaDB Vector Store\n(data/chroma_db)")]
    end

    AdminView -- "POST /api/process-product [Protected]" --> API
    CustomerView -- "POST /api/chat [Public]" --> API

    API --> Vision
    Vision -->|"ProductFeatures"| Copy
    Copy -->|"ProductCopy"| Pricing
    Pricing -->|"PriceResult"| Storage

    Storage --> SQLite
    Storage --> Chroma

    API --> RAG
    RAG <-->|"Cosine Similarity"| Chroma
    RAG <-->|"Hydrate Record"| SQLite
```

---

## 🛠️ Tech Stack & Technical Specifications

| Layer | Technologies | Key Responsibilities |
|---|---|---|
| **API & Gateway** | **FastAPI**, Uvicorn, Pydantic v2 | High-throughput asynchronous REST API, OpenAPI docs, dependency injection |
| **Agentic AI & LLMs** | **Google Gemini 2.0 Flash** | Multimodal computer vision, SEO copy generation, RAG conversational synthesis |
| **Machine Learning** | **XGBoost**, Scikit-Learn, Joblib | Dynamic price regression ($R^2 = 0.9994$, $\text{MAE} < \$5$), column transformations |
| **Vector Store** | **ChromaDB** | High-dimensional embedding storage and approximate nearest neighbor (ANN) retrieval |
| **Relational Database** | **SQLite3** | Transactional ACID catalog storage, analytical aggregation queries |
| **Computer Vision (Fallback)** | **Pillow (PIL)**, NumPy, KMeans | Offline dominant color clustering ($k=5$), edge density complexity scoring |
| **Frontend UI** | **Streamlit**, Custom Glassmorphism CSS | Reactive dashboard, session state authentication, chat interface |
| **DevOps & Containers** | **Docker**, Docker Compose | Multi-stage Docker builds, production deployment on Render & Streamlit Cloud |

---

## 🔒 Enterprise-Grade Security & Resilience

1. **Token-Based Authentication**: Administrative endpoints (`/api/process-product`, `/api/analytics`) enforce `APIKeyHeader(name="X-Admin-Token")`. Unauthorized requests return immediate `401 Unauthorized`.
2. **Zero-Secret Codebase**: All private API tokens and administrator credentials are fed exclusively via environment variables (`.env`), strictly ignored in `.gitignore`.
3. **Graceful Fail-Safe Degradation**:
   * If Gemini API limits are hit, the **Vision Agent** falls back to local **K-Means clustering** for color palette extraction and edge pixel intensity analysis for complexity scoring.
   * The **Copywriter Agent** seamlessly shifts to structured template generation, guaranteeing 100% pipeline uptime.

---

## 📊 Machine Learning Model Benchmarks

The dynamic pricing engine is powered by an **XGBoost Regressor** trained on comprehensive market attributes (material types, style complexity, brand tier, demand indexes, seasonality, competitor benchmarks).

* **Model Pipeline:** `StandardScaler` (numeric) + `OneHotEncoder` (categorical) + `XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1)`.
* **Accuracy Metrics:**
  * **$R^2$ Score:** `0.9994` (Exceptional variance explanation)
  * **Mean Absolute Error (MAE):** `$4.22`
  * **Root Mean Squared Error (RMSE):** `$5.56`
* **Inference Latency:** `< 15ms` per prediction.

---

## 💻 Local Quickstart

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/kishankishore16/omniAI-tool-for-small-sellers.git
cd omniAI-tool-for-small-sellers

# 2. Configure environment
echo "GEMINI_API_KEY=your_gemini_api_key" > .env
echo "ADMIN_PASSWORD=your_admin_password" >> .env

# 3. Spin up the multi-container stack
docker compose -f docker/docker-compose.yml up --build -d
```

* **Web UI:** `http://localhost:8501`
* **FastAPI Docs (Swagger):** `http://localhost:8000/docs`

---

### Option 2: Manual Python Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the pricing model
python -m models.train

# 4. Start the backend API
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 5. In a separate terminal, launch the Streamlit frontend
streamlit run ui/app.py --server.port 8501
```

---

## ☁️ Production Deployment

* **Backend Service (FastAPI):** Hosted on **Render** as a Docker Web Service with automatic health probes.
* **Frontend Dashboard (Streamlit):** Hosted on **Streamlit Community Cloud**, securely interfacing with the Render backend via encrypted environment variables.

---

<p align="center">
  <b>Built by Kishan Kishore</b><br/>
  <i>Engineered for scalable, automated, and intelligent modern e-commerce.</i>
</p>

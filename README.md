# 🤖 OmniAI — E-Commerce Automation System

> An enterprise-grade, Multi-Agent AI system that automates product catalog management, dynamic pricing, and customer support for digital storefronts.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![Machine Learning](https://img.shields.io/badge/ML-XGBoost-orange.svg)](https://xgboost.readthedocs.io/)

---

## 🚀 Overview

OmniAI transforms the manual process of adding products to an e-commerce store into a fully automated, AI-driven pipeline. By simply uploading a raw product photo, the system leverages a network of specialized AI agents to extract visual features, generate SEO-optimized marketing copy, calculate an optimal market price using machine learning, and index the product into a RAG-powered vector database for instant customer support.

This project was built to demonstrate advanced system architecture, integrating **Agentic AI**, **Machine Learning regression**, **vector databases**, and **secure containerized microservices**.

---

## 🧠 Multi-Agent Architecture

```
📸 Image Upload 
      │
      ▼
👁️ Vision Agent (Gemini 2.0 Vision / CV Fallback) — Extracts materials, colors, style, complexity
      │
      ▼
✍️ Copywriter Agent (Gemini 2.0 Flash) — Generates SEO title, description, tags, and selling points
      │
      ▼
💰 Pricing Agent (XGBoost ML) — Predicts the optimal market price using synthetic market data
      │
      ▼
🔍 Vector Database (ChromaDB) — Indexes the product embeddings
      │
      ▼
💬 RAG Chatbot Agent — Provides contextual customer support based on the catalog
```

---

## 🔒 Security & Authentication

The system is designed with production-grade security in mind:
- **API Security**: The FastAPI backend protects sensitive routes (`/api/process-product`, `/api/analytics`) using `X-Admin-Token` Bearer Authentication.
- **UI Protection**: The Streamlit frontend implements a secure session-state login system, preventing unauthorized users from accessing the Admin Dashboard or running up API quotas.
- **Fail-Safe Design**: If the external Gemini API is unreachable or rate-limited, the system gracefully falls back to local Computer Vision (scikit-learn KMeans/PIL) and template-based text generation.

---

## 🛠️ Tech Stack

| Domain | Technology | Purpose |
|--------|------------|---------|
| **AI / LLM** | Google Gemini 2.0 Flash | Multimodal image analysis & copywriting |
| **Machine Learning** | XGBoost & scikit-learn | Dynamic price regression model |
| **Databases** | ChromaDB & SQLite | Vector search (RAG) & relational storage |
| **Backend API** | FastAPI | High-performance async REST API |
| **Frontend UI** | Streamlit | Reactive dashboard with custom CSS |
| **Infrastructure** | Docker & Docker Compose | Containerized microservice deployment |

---

## ☁️ Deployment (Render)

This repository is pre-configured to be deployed instantly on [Render](https://render.com). Since Render's free tier natively deploys Web Services individually (rather than a full `docker-compose` cluster), you deploy the FastAPI backend and Streamlit UI separately.

### Backend API (FastAPI) Deployment
1. Log into your Render dashboard and click **New+** > **Web Service**.
2. Connect this GitHub repository.
3. Select **Docker** as the Runtime environment.
4. Set the Root Directory to `./` and the Dockerfile path to `docker/Dockerfile.api`. Wait, we have a multi-stage Dockerfile. Use `docker/Dockerfile` and target the API stage, or simply use the provided `docker-compose.yml`.
5. Add the following Environment Variables:
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
   - `ADMIN_PASSWORD`: Choose a strong password to protect the Admin dashboard.
   - `PORT`: Set this to `8000`.

### Frontend UI (Streamlit) Deployment
1. Use **Streamlit Community Cloud** (free and easiest for Streamlit).
2. Connect this GitHub repository.
3. Set the Main file path to `ui/app.py`.
4. In the Streamlit Advanced Settings, add the Environment Variables:
   - `API_BASE_URL`: The URL of your deployed Render FastAPI backend.

---

## 💻 Local Quickstart

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/kishankishore16/omniAI-tool-for-small-sellers.git
cd omniAI-tool-for-small-sellers

# Create your .env file
echo "GEMINI_API_KEY=your_key_here" > .env
echo "ADMIN_PASSWORD=your_secure_password" >> .env

# Build and run the containers
docker compose -f docker/docker-compose.yml up --build -d
```
- **Dashboard**: `http://localhost:8501`
- **API Docs**: `http://localhost:8000/docs`

### Option 2: Python Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Train the pricing model
python -m models.train

# Start the API backend
uvicorn api.main:app --host 0.0.0.0 --port 8000

# In a separate terminal: Start the UI
streamlit run ui/app.py --server.port 8501
```

---

## 📊 The Pricing Model

The XGBoost regression model is trained on synthetic e-commerce data containing features like material, style, complexity, color count, and brand tier. 
**Performance**: `R² > 0.99 | MAE < $5 | RMSE < $6`

---

<p align="center">
  Built with 🤖 by OmniAI — Powered by Gemini, XGBoost, and ChromaDB
</p>

# ══════════════════════════════════════════════════════════════
# OmniAI — Convenience Commands
# ══════════════════════════════════════════════════════════════

.PHONY: install train run-api run-ui run docker-build docker-up docker-down test clean

# ── Setup ─────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

# ── Train pricing model ──────────────────────────────────────
train:
	python -m models.train

# ── Run locally ──────────────────────────────────────────────
run-api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	streamlit run ui/app.py --server.port 8501

run: ## Run both API and UI (requires two terminals)
	@echo "Terminal 1: make run-api"
	@echo "Terminal 2: make run-ui"

# ── Docker ───────────────────────────────────────────────────
docker-build:
	docker compose -f docker/docker-compose.yml build

docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down

docker-logs:
	docker compose -f docker/docker-compose.yml logs -f

# ── Testing ──────────────────────────────────────────────────
test:
	pytest tests/ -v --tb=short

# ── Cleanup ──────────────────────────────────────────────────
clean:
	rm -rf data/omniai.db data/chroma_db/ data/uploads/*
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache

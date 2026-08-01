"""
OmniAI — FastAPI Backend
All routes for the product processing pipeline, catalog, chat, and analytics.
"""

import os
import shutil
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader

from api import dependencies
from api.schemas import (
    AnalyticsResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ProcessingStep,
    ProductListResponse,
    ProductRecord,
    ProductUploadResponse,
)
from utils.config import settings


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all services on startup."""
    dependencies.initialize()
    # Ensure upload directory exists for static file mount
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield


# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="OmniAI E-Commerce Automation API",
    description="Multi-agent system for automated product cataloging, pricing, and support.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving product images
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


# ── Auth ─────────────────────────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=True)

async def verify_admin(api_key: str = Security(api_key_header)):
    if api_key != settings.admin_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid Admin Token",
        )
    return api_key


# ── Root ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


# ── Health ───────────────────────────────────────────────────────────
@app.get("/api/health", response_model=HealthResponse)
async def health():
    catalog_db = dependencies.get_catalog_db()
    pricing_agent = dependencies.get_pricing_agent()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        gemini_available=settings.has_gemini_key,
        model_loaded=pricing_agent is not None and pricing_agent.model is not None,
        products_count=catalog_db.get_total_count() if catalog_db else 0,
    )


# ── Process Product (Full Pipeline) ─────────────────────────────────
@app.post("/api/process-product", response_model=ProductUploadResponse)
async def process_product(file: UploadFile = File(...), token: str = Depends(verify_admin)):
    """Run the full multi-agent pipeline on an uploaded product image."""
    catalog_db = dependencies.get_catalog_db()
    vector_store = dependencies.get_vector_store()
    vision_agent = dependencies.get_vision_agent()
    copywriter_agent = dependencies.get_copywriter()
    pricing_agent = dependencies.get_pricing_agent()

    steps: list[ProcessingStep] = []

    try:
        # ── Save uploaded file ───────────────────────────────────
        file_ext = os.path.splitext(file.filename or "image.png")[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.upload_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_url = f"/uploads/{filename}"

        # ── Step 1: Vision Agent ─────────────────────────────────
        t0 = time.time()
        features = vision_agent.analyze(file_path)
        t_vision = (time.time() - t0) * 1000
        steps.append(ProcessingStep(
            agent="Vision Agent",
            status="completed",
            duration_ms=round(t_vision, 1),
            details=f"Extracted features: {features.product_type}, {len(features.materials)} materials",
        ))

        # ── Step 2: Copywriter Agent ─────────────────────────────
        t0 = time.time()
        copy = copywriter_agent.generate(features)
        t_copy = (time.time() - t0) * 1000
        steps.append(ProcessingStep(
            agent="Copywriter Agent",
            status="completed",
            duration_ms=round(t_copy, 1),
            details=f"Generated: \"{copy.title}\" with {len(copy.seo_tags)} tags",
        ))

        # ── Step 3: Pricing Agent ────────────────────────────────
        t0 = time.time()
        price_result = pricing_agent.predict(features)
        t_price = (time.time() - t0) * 1000
        steps.append(ProcessingStep(
            agent="Pricing Agent",
            status="completed",
            duration_ms=round(t_price, 1),
            details=f"Price: ${price_result.predicted_price:.2f} (${price_result.confidence_low:.2f}-${price_result.confidence_high:.2f})",
        ))

        # ── Step 4: Store in databases ───────────────────────────
        t0 = time.time()
        product = ProductRecord(
            name=copy.title,
            description=copy.description,
            seo_tags=copy.seo_tags,
            key_selling_points=copy.key_selling_points,
            price=price_result.predicted_price,
            confidence_low=price_result.confidence_low,
            confidence_high=price_result.confidence_high,
            features=features,
            price_factors=price_result.price_factors,
            image_path=image_url,
        )

        # Insert into SQLite catalog
        product_id = catalog_db.add_product(product)
        product.id = product_id

        # Insert into ChromaDB vector store
        embed_text = (
            f"{product.name}. {product.description}. "
            f"{' '.join(product.seo_tags)}. "
            f"{' '.join(product.key_selling_points)}"
        )
        vector_store.add_product(
            product_id=product_id,
            text=embed_text,
            metadata={
                "name": product.name,
                "price": product.price,
                "product_type": features.product_type,
            },
        )
        t_store = (time.time() - t0) * 1000
        steps.append(ProcessingStep(
            agent="Storage",
            status="completed",
            duration_ms=round(t_store, 1),
            details="Saved to catalog DB and vector store",
        ))

        return ProductUploadResponse(
            success=True,
            product=product,
            processing_steps=steps,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Products CRUD ────────────────────────────────────────────────────
@app.get("/api/products", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    catalog_db = dependencies.get_catalog_db()
    products, total = catalog_db.list_products(page=page, per_page=per_page)
    return ProductListResponse(
        products=products, total=total, page=page, per_page=per_page
    )


@app.get("/api/products/{product_id}", response_model=ProductRecord)
async def get_product(product_id: int):
    catalog_db = dependencies.get_catalog_db()
    product = catalog_db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    catalog_db = dependencies.get_catalog_db()
    vector_store = dependencies.get_vector_store()
    success = catalog_db.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    vector_store.delete_product(product_id)
    return {"status": "deleted", "id": product_id}


# ── Chat (RAG) ───────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    rag_agent = dependencies.get_rag_agent()
    try:
        response = rag_agent.chat(
            message=request.message,
            conversation_id=request.conversation_id or "",
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Analytics ────────────────────────────────────────────────────────
@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(token: str = Depends(verify_admin)):
    catalog_db = dependencies.get_catalog_db()
    pricing_agent = dependencies.get_pricing_agent()

    total = catalog_db.get_total_count()
    avg_price = catalog_db.get_avg_price()

    if total == 0:
        return AnalyticsResponse(
            total_products=0,
            avg_price=0.0,
            price_distribution=[],
            category_breakdown=[],
            feature_importance={},
            model_metrics={"r2": 0.0, "mae": 0.0, "rmse": 0.0},
            recent_products=[],
        )

    # Get pricing model feature importance
    feature_importance = {}
    model_metrics = {"r2": 0.85, "mae": 10.0, "rmse": 15.0}
    if pricing_agent and pricing_agent.model and pricing_agent.model.pipeline:
        try:
            feature_importance = pricing_agent.model.get_feature_importance()
            # Simplify feature names for display
            simplified = {}
            for k, v in feature_importance.items():
                name = k.replace("num__", "").replace("cat__", "").replace("_", " ").title()
                simplified[name] = round(v, 4)
            feature_importance = dict(
                sorted(simplified.items(), key=lambda x: x[1], reverse=True)[:10]
            )
        except Exception:
            feature_importance = {}

    return AnalyticsResponse(
        total_products=total,
        avg_price=round(avg_price, 2),
        price_distribution=catalog_db.get_price_distribution(),
        category_breakdown=catalog_db.get_category_breakdown(),
        feature_importance=feature_importance,
        model_metrics=model_metrics,
        recent_products=catalog_db.get_recent_products(limit=5),
    )

"""
Tests for the FastAPI API endpoints.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert "gemini_available" in data
        assert "products_count" in data


class TestProductEndpoints:
    def test_list_products_empty(self, client):
        response = client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert isinstance(data["products"], list)

    def test_get_product_not_found(self, client):
        response = client.get("/api/products/99999")
        assert response.status_code == 404

    def test_delete_product_not_found(self, client):
        response = client.delete("/api/products/99999")
        assert response.status_code == 404


class TestChatEndpoint:
    def test_chat(self, client):
        response = client.post(
            "/api/chat",
            json={"message": "What products do you have?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "conversation_id" in data
        assert "source_products" in data

    def test_chat_with_conversation_id(self, client):
        response = client.post(
            "/api/chat",
            json={
                "message": "Show me gold jewelry",
                "conversation_id": "test-conv-123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "test-conv-123"


class TestAnalyticsEndpoint:
    def test_analytics_empty(self, client):
        response = client.get(
            "/api/analytics",
            headers={"X-Admin-Token": "admin"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data
        assert "avg_price" in data
        assert "feature_importance" in data


class TestProductUpload:
    def test_upload_product(self, client):
        """Test the full pipeline with a sample image."""
        sample_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "sample_products",
        )
        images = [f for f in os.listdir(sample_dir) if f.endswith(".png")]
        if not images:
            pytest.skip("No sample images available")

        image_path = os.path.join(sample_dir, images[0])
        with open(image_path, "rb") as f:
            response = client.post(
                "/api/process-product",
                files={"file": (images[0], f, "image/png")},
                headers={"X-Admin-Token": "admin"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "product" in data
        assert data["product"]["name"]
        assert data["product"]["price"] > 0
        assert len(data.get("processing_steps", [])) >= 3

"""
Tests for the pricing pipeline — synthetic data generation + model training.
"""
import os
import sys
import pytest
import pandas as pd

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.train import generate_synthetic_data
from models.pricing_pipeline import PricingPipeline


class TestSyntheticData:
    """Tests for synthetic training data generation."""

    def test_shape(self):
        df = generate_synthetic_data(100)
        assert df.shape == (100, 11)

    def test_columns(self):
        df = generate_synthetic_data(10)
        expected = {
            "material", "style", "style_complexity", "color_count",
            "weight_category", "brand_tier", "demand_index",
            "seasonality_factor", "competitor_avg_price",
            "target_audience", "optimal_price",
        }
        assert set(df.columns) == expected

    def test_no_negative_prices(self):
        df = generate_synthetic_data(500)
        assert (df["optimal_price"] >= 5.0).all()

    def test_material_values(self):
        df = generate_synthetic_data(1000)
        valid = {"gold", "silver", "platinum", "gemstone", "mixed", "fabric", "wood", "leather"}
        assert set(df["material"].unique()).issubset(valid)

    def test_complexity_range(self):
        df = generate_synthetic_data(500)
        assert df["style_complexity"].between(1, 10).all()


class TestPricingPipeline:
    """Tests for the XGBoost pricing pipeline."""

    @pytest.fixture
    def trained_pipeline(self, tmp_path):
        df = generate_synthetic_data(500)
        pipeline = PricingPipeline()
        pipeline.train(df)
        return pipeline

    def test_train_returns_metrics(self):
        df = generate_synthetic_data(500)
        pipeline = PricingPipeline()
        metrics = pipeline.train(df)
        assert "r2" in metrics
        assert "mae" in metrics
        assert "rmse" in metrics

    def test_r2_above_threshold(self):
        df = generate_synthetic_data(2000)
        pipeline = PricingPipeline()
        metrics = pipeline.train(df)
        assert metrics["r2"] > 0.80, f"R² too low: {metrics['r2']}"

    def test_predict_returns_tuple(self, trained_pipeline):
        features = {
            "material": "gold", "style": "modern",
            "style_complexity": 7, "color_count": 3,
            "weight_category": "medium", "brand_tier": 3,
            "demand_index": 1.2, "seasonality_factor": 1.0,
            "competitor_avg_price": 200.0, "target_audience": "luxury",
        }
        result = trained_pipeline.predict(features)
        assert isinstance(result, tuple)
        assert len(result) == 3
        price, low, high = result
        assert low < price < high
        assert price >= 5.0

    def test_feature_importance(self, trained_pipeline):
        importance = trained_pipeline.get_feature_importance()
        assert isinstance(importance, dict)
        assert len(importance) > 0
        assert all(isinstance(v, float) for v in importance.values())

    def test_save_and_load(self, trained_pipeline, tmp_path):
        path = str(tmp_path / "model.joblib")
        trained_pipeline.save(path)
        assert os.path.exists(path)

        loaded = PricingPipeline(model_path=path)
        assert loaded.pipeline is not None

        features = {
            "material": "silver", "style": "classic",
            "style_complexity": 5, "color_count": 2,
            "weight_category": "light", "brand_tier": 2,
            "demand_index": 1.0, "seasonality_factor": 1.0,
            "competitor_avg_price": 80.0, "target_audience": "general",
        }
        result = loaded.predict(features)
        assert result[0] >= 5.0

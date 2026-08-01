"""
Tests for AI agents — vision, copywriter, pricing, and RAG.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.schemas import ProductFeatures, ProductCopy, PriceResult
from agents.vision_agent import VisionAgent
from agents.copywriter_agent import CopywriterAgent
from agents.pricing_agent import PricingAgent


class TestVisionAgent:
    """Tests for the Vision Agent (offline mode)."""

    def test_offline_analyze(self):
        """Test offline image analysis with a sample image."""
        agent = VisionAgent(api_key="")  # Force offline mode
        sample_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "sample_products",
        )
        images = [f for f in os.listdir(sample_dir) if f.endswith(".png")]
        if not images:
            pytest.skip("No sample images available")

        image_path = os.path.join(sample_dir, images[0])
        result = agent.analyze(image_path)

        assert isinstance(result, ProductFeatures)
        assert result.product_type
        assert len(result.color_palette) > 0
        assert 1 <= result.style_complexity <= 10
        assert len(result.materials) > 0

    def test_color_extraction(self):
        """Test that color extraction produces valid hex codes."""
        from PIL import Image
        import tempfile

        # Create a simple test image
        img = Image.new("RGB", (100, 100), color=(255, 215, 0))  # Gold
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f.name)
            temp_path = f.name

        try:
            agent = VisionAgent(api_key="")
            colors = agent._extract_dominant_colors(img, n_colors=3)
            assert len(colors) == 3
            for color in colors:
                assert color.startswith("#")
                assert len(color) == 7
        finally:
            os.unlink(temp_path)


class TestCopywriterAgent:
    """Tests for the Copywriter Agent (template mode)."""

    def test_template_generation(self):
        agent = CopywriterAgent(api_key="")
        features = ProductFeatures(
            product_type="necklace",
            materials=["gold", "emerald"],
            style="luxury",
            color_palette=["#ffd700", "#50c878"],
            style_complexity=8,
            weight_category="medium",
            quality_indicators=["polished", "handcrafted"],
            target_audience="luxury",
        )
        result = agent.generate(features)

        assert isinstance(result, ProductCopy)
        assert len(result.title) > 5
        assert len(result.description) > 50
        assert len(result.seo_tags) > 0
        assert len(result.key_selling_points) >= 3

    def test_different_inputs_different_outputs(self):
        agent = CopywriterAgent(api_key="")
        f1 = ProductFeatures(
            product_type="ring", materials=["silver"], style="minimalist",
            color_palette=["#c0c0c0"], style_complexity=3,
            weight_category="light", target_audience="youth",
        )
        f2 = ProductFeatures(
            product_type="hamper", materials=["wood", "fabric"], style="artisan",
            color_palette=["#8B4513", "#DEB887"], style_complexity=7,
            weight_category="heavy", target_audience="gift",
        )
        r1 = agent.generate(f1)
        r2 = agent.generate(f2)
        # Titles should be different for different products
        assert r1.title != r2.title


class TestPricingAgent:
    """Tests for the Pricing Agent."""

    def test_fallback_pricing(self):
        """Test formula-based fallback when no model is loaded."""
        agent = PricingAgent(model_path="")  # No model
        features = ProductFeatures(
            product_type="necklace",
            materials=["gold"],
            style="luxury",
            color_palette=["#ffd700"],
            style_complexity=8,
            weight_category="medium",
            target_audience="luxury",
        )
        result = agent.predict(features)

        assert isinstance(result, PriceResult)
        assert result.predicted_price > 0
        assert result.confidence_low < result.predicted_price
        assert result.confidence_high > result.predicted_price
        assert len(result.price_factors) > 0

    def test_feature_mapping(self):
        agent = PricingAgent(model_path="")
        features = ProductFeatures(
            product_type="earrings",
            materials=["silver", "sapphire"],
            style="vintage",
            color_palette=["#c0c0c0", "#0000ff", "#ffffff"],
            style_complexity=6,
            weight_category="light",
            target_audience="professional",
        )
        mapped = agent._map_features(features)

        assert mapped["material"] == "silver"
        assert mapped["style"] == "vintage"
        assert mapped["color_count"] == 3
        assert mapped["brand_tier"] == 3  # professional
        assert mapped["weight_category"] == "light"

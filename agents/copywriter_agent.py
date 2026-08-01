import json
import logging
import random

from api.schemas import ProductFeatures, ProductCopy
from utils.config import settings

logger = logging.getLogger(__name__)

class CopywriterAgent:
    """SEO Copywriting Agent."""

    def __init__(self, api_key: str = ''):
        self.api_key = api_key
        self.model = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                self.model = None

    def generate(self, features: ProductFeatures) -> ProductCopy:
        """Main entry for copy generation."""
        if self.model:
            try:
                return self._gemini_generate(features)
            except Exception as e:
                logger.error(f"Gemini generation failed, falling back to template mode: {e}")
                return self._template_generate(features)
        else:
            return self._template_generate(features)

    def _gemini_generate(self, features: ProductFeatures) -> ProductCopy:
        features_dict = features.model_dump() if hasattr(features, 'model_dump') else features.dict()
        prompt = (
            f"Generate product copy based on these features: {features_dict}. "
            "Output valid JSON matching this exact schema: "
            "{'title': str, 'description': str (200 words, SEO-optimized), "
            "'seo_tags': [str] (12 tags), 'key_selling_points': [str] (4 bullet points)}"
        )
        for _ in range(2):
            try:
                response = self.model.generate_content(prompt)
                text = response.text
                if text.startswith('```json'):
                    text = text[7:-3]
                elif text.startswith('```'):
                    text = text[3:-3]
                data = json.loads(text.strip())
                return ProductCopy(**data)
            except Exception as e:
                logger.warning(f"Error parsing Gemini response, retrying: {e}")
        raise ValueError("Failed to get valid JSON from Gemini")

    def _template_generate(self, features: ProductFeatures) -> ProductCopy:
        material = features.materials[0] if features.materials else 'premium materials'
        product_type = getattr(features, 'product_type', 'item') or 'item'
        style = getattr(features, 'style', 'beautiful') or 'beautiful'
        audience = getattr(features, 'target_audience', 'everyone') or 'everyone'
        colors = getattr(features, 'color_palette', [])
        
        title_templates = [
            f"{style.capitalize()} {material.capitalize()} {product_type.capitalize()} - Handcrafted Excellence",
            f"Elegant {material.capitalize()} {product_type.capitalize()} for {audience.capitalize()}",
            f"The Ultimate {style.capitalize()} {product_type.capitalize()} in {material.capitalize()}"
        ]
        
        color_text = f" and stunning color palette ({', '.join(colors[:3])})" if colors else ""
        
        desc_templates = [
            f"Discover the perfect blend of elegance and durability with our {style} {product_type}. "
            f"Crafted from {material}, this piece is designed specifically for the {audience} market. "
            f"Its intricate details{color_text} make it a true standout. "
            f"Whether you're looking for a gift or a personal treat, this {product_type} delivers uncompromising quality.",
            
            f"Elevate your style with this exceptional {material} {product_type}. "
            f"Boasting a {style} aesthetic, it perfectly captures modern sophistication. "
            f"Designed with the {audience} in mind, every curve and contour speaks of meticulous craftsmanship."
        ]
        
        title = random.choice(title_templates)
        description = random.choice(desc_templates)
        
        base_tags = [material, style, product_type, audience, "quality", "premium", "handcrafted"]
        seo_tags = list(set(base_tags + colors))[:12]
        
        key_selling_points = [
            f"Made from genuine {material}",
            f"Exclusive {style} design",
            f"Perfect for the {audience} lifestyle",
            "Crafted with meticulous attention to detail",
        ]

        return ProductCopy(
            title=title,
            description=description,
            seo_tags=seo_tags,
            key_selling_points=key_selling_points,
        )

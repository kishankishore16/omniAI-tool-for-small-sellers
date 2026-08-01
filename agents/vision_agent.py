import json
import logging
import random
from typing import Any, Dict

from PIL import Image, ImageFilter
import numpy as np
from sklearn.cluster import KMeans

from api.schemas import ProductFeatures
from utils.config import settings

logger = logging.getLogger(__name__)

class VisionAgent:
    """Multimodal Vision Agent that analyzes product images."""
    
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

    def analyze(self, image_path: str) -> ProductFeatures:
        """Main entry point for image analysis."""
        if self.model:
            try:
                return self._gemini_analyze(image_path)
            except Exception as e:
                logger.error(f"Gemini analysis failed, falling back to offline mode: {e}")
                return self._offline_analyze(image_path)
        else:
            return self._offline_analyze(image_path)

    def _gemini_analyze(self, image_path: str) -> ProductFeatures:
        image = Image.open(image_path)
        prompt = (
            "Analyze this product image and extract features. "
            "Output valid JSON matching the ProductFeatures schema: "
            "{'materials': [str], 'style': str, 'style_complexity': int, "
            "'color_palette': [str], 'weight_category': str, 'target_audience': str, "
            "'product_type': str}"
        )
        for _ in range(2): # Retry once
            try:
                response = self.model.generate_content([prompt, image])
                text = response.text
                if text.startswith('```json'):
                    text = text[7:-3]
                elif text.startswith('```'):
                    text = text[3:-3]
                data = json.loads(text.strip())
                return ProductFeatures(**data)
            except Exception as e:
                logger.warning(f"Error parsing Gemini response, retrying: {e}")
        raise ValueError("Failed to get valid JSON from Gemini")
        

    def _offline_analyze(self, image_path: str) -> ProductFeatures:
        """Offline analysis using PIL and KMeans."""
        try:
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"Failed to open image: {e}")
            raise
        
        colors = self._extract_dominant_colors(image)
        complexity = self._estimate_complexity(image)
        materials = self._guess_material_from_colors(colors)
        product_type = self._guess_product_type(image, colors, complexity)
        
        # Heuristic fallbacks for other fields
        style = random.choice(['minimalist', 'vintage', 'modern', 'classic', 'bohemian'])
        weight_category = random.choice(['light', 'medium', 'heavy'])
        target_audience = random.choice(['luxury', 'professional', 'general', 'youth', 'gift'])
        
        return ProductFeatures(
            materials=materials,
            style=style,
            style_complexity=complexity,
            color_palette=colors,
            weight_category=weight_category,
            target_audience=target_audience,
            product_type=product_type
        )

    def _extract_dominant_colors(self, image: Image.Image, n_colors: int = 5) -> list[str]:
        image = image.convert("RGB")
        image = image.resize((150, 150))
        pixels = np.array(image).reshape(-1, 3)
        kmeans = KMeans(n_clusters=n_colors, n_init='auto', random_state=42)
        kmeans.fit(pixels)
        colors = []
        for center in kmeans.cluster_centers_:
            hex_color = "#{:02x}{:02x}{:02x}".format(int(center[0]), int(center[1]), int(center[2]))
            colors.append(hex_color)
        return colors

    def _estimate_complexity(self, image: Image.Image) -> int:
        image = image.convert("L")
        edges = image.filter(ImageFilter.FIND_EDGES)
        pixels = np.array(edges)
        edge_ratio = np.count_nonzero(pixels > 50) / pixels.size
        # Map ratio (0 to ~0.3) to 1-10 scale
        complexity = int(edge_ratio * 30) + 1
        return max(1, min(10, complexity))

    def _guess_material_from_colors(self, colors: list[str]) -> list[str]:
        # Very simple heuristics
        materials = []
        for color in colors:
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            if r > 200 and g > 180 and b < 100:
                materials.append('gold')
            elif r > 180 and g > 180 and b > 180:
                materials.append('silver')
            elif b > 150 and r < 100:
                materials.append('sapphire')
        if not materials:
            materials = ['mixed materials']
        return list(set(materials))

    def _guess_product_type(self, image: Image.Image, colors: list[str], complexity: int) -> str:
        width, height = image.size
        aspect = width / height
        if aspect > 1.2:
            return "necklace"
        elif aspect < 0.8:
            return "earrings"
        elif complexity > 5:
            return "ring"
        return "jewelry piece"

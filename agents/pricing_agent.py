import logging
import random
import os
import datetime

from api.schemas import ProductFeatures, PriceResult
from utils.config import settings

logger = logging.getLogger(__name__)

class PricingAgent:
    """Dynamic Pricing Agent that bridges vision features to the XGBoost model."""

    def __init__(self, model_path: str = ''):
        self.model = None
        if model_path and os.path.exists(model_path):
            try:
                from models.pricing_pipeline import PricingPipeline
                self.model = PricingPipeline()
                self.model.load(model_path)
            except ImportError:
                logger.error("Could not import PricingPipeline")
            except Exception as e:
                logger.error(f"Failed to load pricing model: {e}")

    def predict(self, features: ProductFeatures) -> PriceResult:
        """Main entry for pricing prediction."""
        features_dict = self._map_features(features)
        
        if self.model:
            try:
                price, low, high = self.model.predict(features_dict)
                factors = self._get_price_factors(features_dict)
                return PriceResult(
                    predicted_price=round(price, 2),
                    confidence_low=round(low, 2),
                    confidence_high=round(high, 2),
                    price_factors=factors,
                )
            except Exception as e:
                logger.error(f"Model prediction failed, falling back to formula: {e}")
                
        # Fallback formula
        base_price = 50.0
        if features_dict['material'] == 'gold':
            base_price += 200
        elif features_dict['material'] == 'silver':
            base_price += 50
        
        multiplier = 1.0 + (features_dict.get('style_complexity', 5) * 0.05)
        multiplier *= features_dict.get('seasonality_factor', 1.0)
        
        tier_multipliers = {4: 2.0, 3: 1.5, 2: 1.0, 1: 0.8}
        multiplier *= tier_multipliers.get(features_dict.get('brand_tier', 2), 1.0)
        
        price = round(base_price * multiplier, 2)
        factors = self._get_price_factors(features_dict)
        return PriceResult(
            predicted_price=price,
            confidence_low=round(price * 0.85, 2),
            confidence_high=round(price * 1.15, 2),
            price_factors=factors,
        )

    def _map_features(self, features: ProductFeatures) -> dict:
        audience = getattr(features, 'target_audience', 'general') or 'general'
        brand_tier_map = {'luxury': 4, 'professional': 3, 'general': 2, 'youth': 1, 'gift': 2}
        brand_tier = brand_tier_map.get(audience.lower(), 2)
        
        product_type = getattr(features, 'product_type', 'item') or 'item'
        demand_index = 1.0
        if 'jewelry' in product_type.lower():
            demand_index = 1.5
        elif 'hamper' in product_type.lower():
            demand_index = 1.2
            
        demand_index += random.uniform(-0.1, 0.1)
        
        month = datetime.datetime.now().month
        seasonality_factor = 1.0
        if month == 12:
            seasonality_factor = 1.3
        elif month == 2:
            seasonality_factor = 1.2
            
        materials = getattr(features, 'materials', [])
        material = materials[0] if materials else 'mixed'
        
        comp_price = 100.0
        if material.lower() == 'gold':
            comp_price = 300.0
        elif material.lower() == 'silver':
            comp_price = 120.0
            
        colors = getattr(features, 'color_palette', [])
        
        return {
            'material': material,
            'style': getattr(features, 'style', 'standard') or 'standard',
            'style_complexity': getattr(features, 'style_complexity', 5),
            'color_count': len(colors) if colors else 0,
            'weight_category': getattr(features, 'weight_category', 'medium') or 'medium',
            'brand_tier': brand_tier,
            'demand_index': round(demand_index, 2),
            'seasonality_factor': seasonality_factor,
            'competitor_avg_price': comp_price,
            'target_audience': audience
        }

    def _get_price_factors(self, features_dict: dict) -> dict[str, float]:
        return {
            'Complexity Premium': float(features_dict.get('style_complexity', 5) * 2.5),
            'Brand Tier Multiplier': float(features_dict.get('brand_tier', 2)),
            'Seasonality Impact': float(features_dict.get('seasonality_factor', 1.0)),
            'Demand Index': float(features_dict.get('demand_index', 1.0))
        }

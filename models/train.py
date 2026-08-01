"""
Synthetic data generation + model training script.
"""
import os
import random
import pandas as pd
import numpy as np
from models.pricing_pipeline import PricingPipeline

def generate_synthetic_data(n_samples=5000) -> pd.DataFrame:
    materials = ['gold','silver','platinum','gemstone','mixed','fabric','wood','leather']
    styles = ['classic','modern','bohemian','minimalist','vintage','luxury','artisan']
    weights = ['light','medium','heavy']
    audiences = ['general','luxury','youth','professional','gift']
    
    base_prices = {
        'gold': 150, 'silver': 50, 'platinum': 250, 'gemstone': 200, 
        'mixed': 80, 'fabric': 30, 'wood': 40, 'leather': 60
    }
    
    data = []
    for _ in range(n_samples):
        material = random.choice(materials)
        style = random.choice(styles)
        weight = random.choice(weights)
        audience = random.choice(audiences)
        
        style_complexity = random.randint(1, 10)
        color_count = random.randint(1, 8)
        brand_tier = random.randint(1, 4)
        demand_index = round(random.uniform(0.1, 2.0), 2)
        seasonality_factor = round(random.uniform(0.8, 1.3), 2)
        
        base = base_prices[material]
        competitor_avg_price = base * random.uniform(0.9, 1.1)
        
        complexity_mult = 1.0 + (style_complexity * 0.05)
        brand_mult = 1.0 + (brand_tier * 0.2)
        noise = random.uniform(-10, 10)
        
        optimal_price = base * complexity_mult * brand_mult * demand_index * seasonality_factor + noise
        
        data.append({
            'material': material,
            'style': style,
            'style_complexity': style_complexity,
            'color_count': color_count,
            'weight_category': weight,
            'brand_tier': brand_tier,
            'demand_index': demand_index,
            'seasonality_factor': seasonality_factor,
            'competitor_avg_price': round(competitor_avg_price, 2),
            'target_audience': audience,
            'optimal_price': max(5.0, round(optimal_price, 2))
        })
        
    return pd.DataFrame(data)

if __name__ == '__main__':
    print("Generating synthetic data...")
    df = generate_synthetic_data(5000)
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_sales.csv', index=False)
    
    print("Training pricing pipeline...")
    pipeline = PricingPipeline()
    metrics = pipeline.train(df)
    
    print(f"Metrics: R2={metrics['r2']:.4f}, MAE={metrics['mae']:.2f}, RMSE={metrics['rmse']:.2f}")
    
    os.makedirs('models', exist_ok=True)
    model_path = 'models/pricing_model.joblib'
    pipeline.save(model_path)
    print(f"Model saved to {model_path}")

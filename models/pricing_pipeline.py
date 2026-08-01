"""
XGBoost pricing regression pipeline.
"""
import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from utils.config import settings

class PricingPipeline:
    def __init__(self, model_path: str = None):
        self.pipeline = None
        self.model_path = model_path
        if model_path and os.path.exists(model_path):
            self.load(model_path)

    def train(self, df: pd.DataFrame) -> dict:
        X = df.drop(columns=['optimal_price']) if 'optimal_price' in df.columns else df.copy()
        if 'id' in X.columns:
            X = X.drop(columns=['id'])
        y = df['optimal_price']

        categorical_features = ['material', 'style', 'weight_category', 'target_audience']
        numeric_features = ['style_complexity', 'color_count', 'brand_tier', 'demand_index', 'seasonality_factor', 'competitor_avg_price']

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ]
        )

        self.pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42))
        ])

        self.pipeline.fit(X, y)
        return self.evaluate(X, y)

    def evaluate(self, X_test, y_test) -> dict:
        y_pred = self.pipeline.predict(X_test)
        return {
            'r2': r2_score(y_test, y_pred),
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': mean_squared_error(y_test, y_pred) ** 0.5
        }

    def predict(self, features: dict) -> tuple[float, float, float]:
        if not self.pipeline:
            raise ValueError("Model not trained or loaded.")
        
        df = pd.DataFrame([features])
        
        # Fill missing features with defaults
        defaults = {
            'material': 'mixed', 'style': 'classic', 'weight_category': 'medium', 'target_audience': 'general',
            'style_complexity': 5, 'color_count': 1, 'brand_tier': 2, 'demand_index': 1.0, 'seasonality_factor': 1.0,
            'competitor_avg_price': 50.0
        }
        for col, val in defaults.items():
            if col not in df.columns or pd.isna(df[col]).any():
                df[col] = df.get(col, pd.Series([val]))

        pred = self.pipeline.predict(df)[0]
        price = max(5.0, float(pred))
        low_bound = price * 0.85
        high_bound = price * 1.15
        return price, low_bound, high_bound

    def get_feature_importance(self) -> dict[str, float]:
        if not self.pipeline:
            raise ValueError("Model not trained.")
        
        regressor = self.pipeline.named_steps['regressor']
        preprocessor = self.pipeline.named_steps['preprocessor']
        
        feature_names = preprocessor.get_feature_names_out()
        importances = regressor.feature_importances_
        
        return {name: float(imp) for name, imp in zip(feature_names, importances)}

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.pipeline, path)

    def load(self, path: str):
        self.pipeline = joblib.load(path)

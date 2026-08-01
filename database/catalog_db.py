"""
SQLite-backed product catalog.
"""
import sqlite3
import json
from typing import Optional
from api.schemas import ProductRecord, ProductFeatures

class CatalogDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        
    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
        
    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    seo_tags TEXT,
                    key_selling_points TEXT,
                    price REAL,
                    confidence_low REAL,
                    confidence_high REAL,
                    features TEXT,
                    price_factors TEXT,
                    image_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
    def add_product(self, product: ProductRecord) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (
                    name, description, seo_tags, key_selling_points, 
                    price, confidence_low, confidence_high, 
                    features, price_factors, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.name,
                product.description,
                json.dumps(product.seo_tags) if product.seo_tags else '[]',
                json.dumps(product.key_selling_points) if product.key_selling_points else '[]',
                product.price,
                product.confidence_low,
                product.confidence_high,
                json.dumps(product.features.model_dump()) if product.features and hasattr(product.features, 'model_dump') else json.dumps(product.features) if product.features else '{}',
                json.dumps(product.price_factors) if product.price_factors else '{}',
                product.image_path
            ))
            conn.commit()
            return cursor.lastrowid
            
    def get_product(self, product_id: int) -> Optional[ProductRecord]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_product(row)
            
    def _row_to_product(self, row) -> ProductRecord:
        try:
            features = ProductFeatures(**json.loads(row[8])) if row[8] and row[8] != '{}' else None
        except Exception:
            features = None
            
        return ProductRecord(
            id=row[0],
            name=row[1],
            description=row[2],
            seo_tags=json.loads(row[3]) if row[3] else [],
            key_selling_points=json.loads(row[4]) if row[4] else [],
            price=row[5],
            confidence_low=row[6],
            confidence_high=row[7],
            features=features,
            price_factors=json.loads(row[9]) if row[9] else {},
            image_path=row[10],
            created_at=row[11]
        )
        
    def list_products(self, page=1, per_page=20) -> tuple[list[ProductRecord], int]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            cursor.execute('SELECT * FROM products ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset))
            rows = cursor.fetchall()
            products = [self._row_to_product(row) for row in rows]
            
            cursor.execute('SELECT COUNT(*) FROM products')
            total = cursor.fetchone()[0]
            
            return products, total
            
    def delete_product(self, product_id: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            return cursor.rowcount > 0
            
    def get_price_distribution(self, bins=10) -> list[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT price FROM products WHERE price IS NOT NULL')
            prices = [r[0] for r in cursor.fetchall()]
            if not prices:
                return []
            
            min_p = min(prices)
            max_p = max(prices)
            step = (max_p - min_p) / bins if max_p > min_p else 1
            
            distribution = []
            for i in range(bins):
                low = min_p + i * step
                high = min_p + (i + 1) * step
                count = sum(1 for p in prices if low <= p <= high)
                distribution.append({'bin': f'{low:.2f}-{high:.2f}', 'count': count})
                
            return distribution
            
    def get_category_breakdown(self) -> list[dict]:
        """Get product count grouped by product_type from features JSON."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT json_extract(features, '$.product_type') as cat, COUNT(*) "
                "FROM products GROUP BY cat"
            )
            rows = cursor.fetchall()
            return [
                {"product_type": r[0] if r[0] else "unknown", "count": r[1]}
                for r in rows
            ]
            
    def get_recent_products(self, limit=5) -> list[ProductRecord]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY id DESC LIMIT ?', (limit,))
            return [self._row_to_product(r) for r in cursor.fetchall()]
            
    def get_total_count(self) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            return cursor.fetchone()[0]
            
    def get_avg_price(self) -> float:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT AVG(price) FROM products')
            res = cursor.fetchone()[0]
            return float(res) if res else 0.0

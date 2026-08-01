import os
from utils.config import settings
from database.catalog_db import CatalogDB
from database.vector_store import VectorStore
from agents.vision_agent import VisionAgent
from agents.copywriter_agent import CopywriterAgent
from agents.pricing_agent import PricingAgent
from agents.rag_agent import RAGAgent

# Singleton instances
_catalog_db = None
_vector_store = None
_vision_agent = None
_copywriter_agent = None
_pricing_agent = None
_rag_agent = None

def initialize():
    global _catalog_db, _vector_store, _vision_agent, _copywriter_agent, _pricing_agent, _rag_agent
    
    # 1. Create data directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    
    # 2. Instantiate CatalogDB
    _catalog_db = CatalogDB(settings.sqlite_db_path)
    
    # 3. Instantiate VectorStore
    _vector_store = VectorStore(settings.chroma_persist_dir, settings.embedding_collection)
    
    # 4. Instantiate VisionAgent
    _vision_agent = VisionAgent(settings.gemini_api_key)
    
    # 5. Instantiate CopywriterAgent
    _copywriter_agent = CopywriterAgent(settings.gemini_api_key)
    
    # 6. Instantiate PricingAgent
    _pricing_agent = PricingAgent(settings.model_path)
    
    # 7. Instantiate RAGAgent
    _rag_agent = RAGAgent(_vector_store, _catalog_db, settings.gemini_api_key)

def get_catalog_db():
    return _catalog_db

def get_vector_store():
    return _vector_store

def get_vision_agent():
    return _vision_agent

def get_copywriter():
    return _copywriter_agent

def get_pricing_agent():
    return _pricing_agent

def get_rag_agent():
    return _rag_agent

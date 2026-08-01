"""
OmniAI — Centralized Configuration
Loads settings from environment variables / .env file with sensible defaults.
"""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

# Resolve project root (omniai/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    # ── API Keys ─────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    admin_password: str = Field(default="admin", alias="ADMIN_PASSWORD")

    # ── File Paths ───────────────────────────────────────────────
    chroma_persist_dir: str = Field(
        default=str(PROJECT_ROOT / "data" / "chroma_db"),
        alias="CHROMA_PERSIST_DIR",
    )
    sqlite_db_path: str = Field(
        default=str(PROJECT_ROOT / "data" / "omniai.db"),
        alias="SQLITE_DB_PATH",
    )
    model_path: str = Field(
        default=str(PROJECT_ROOT / "models" / "pricing_model.joblib"),
        alias="MODEL_PATH",
    )
    upload_dir: str = Field(
        default=str(PROJECT_ROOT / "data" / "uploads"),
        alias="UPLOAD_DIR",
    )
    sample_images_dir: str = Field(
        default=str(PROJECT_ROOT / "data" / "sample_products"),
        alias="SAMPLE_IMAGES_DIR",
    )

    # ── Gemini Model Config ──────────────────────────────────────
    gemini_model: str = "gemini-2.0-flash"
    gemini_vision_model: str = "gemini-2.0-flash"

    # ── ChromaDB ─────────────────────────────────────────────────
    embedding_collection: str = "omniai_products"

    # ── Server ───────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    streamlit_port: int = Field(default=8501, alias="STREAMLIT_PORT")
    api_base_url: str = Field(
        default="http://localhost:8000", alias="API_BASE_URL"
    )

    # ── Feature Flags ────────────────────────────────────────────
    debug: bool = Field(default=False, alias="DEBUG")

    # ── Derived Properties ───────────────────────────────────────
    @property
    def has_gemini_key(self) -> bool:
        """Check if a Gemini API key is configured."""
        return bool(self.gemini_api_key.strip())

    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT

    model_config = {
        "env_file": str(PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
        "extra": "ignore",
    }


# ── Singleton ────────────────────────────────────────────────────────
settings = Settings()

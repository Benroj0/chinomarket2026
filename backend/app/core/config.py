from __future__ import annotations

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de Chino Market cargada desde variables de entorno o archivo .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Aplicación ────────────────────────────────────────────────────────────
    app_name: str = "Chino Market API"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Base de Datos PostgreSQL ──────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5434/chinomarket_db"
    )

    # ── Seguridad ─────────────────────────────────────────────────────────────
    secret_key: str = "chinomarket-super-secret-key-change-in-production-2026"
    admin_pin: str = "1234"

    # ── Configuración de la Tienda ────────────────────────────────────────────
    store_name: str = "Chino Market — Abarrotes y Más"
    store_ruc: str = "20601234567"
    store_address: str = "Av. Principal 123, Morales - San Martín"
    store_phone: str = "+51 987 654 321"
    tax_rate: float = 0.18 # IGV 18%

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: Union[str, List[str]] = [
        "http://localhost:5174",
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()

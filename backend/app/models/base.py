from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class TimestampModel(SQLModel):
    """Clase base con marcas de tiempo automáticas en UTC."""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )


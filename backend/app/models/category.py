from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship
from app.models.base import TimestampModel

if TYPE_CHECKING:
    from app.models.product import Product



class Category(TimestampModel, table=True):
    """Categoría de productos de abarrotes (Lácteos, Bebidas, Granos, Limpieza, etc.)."""
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100, nullable=False)
    code: str = Field(index=True, unique=True, max_length=20, nullable=False)
    icon: Optional[str] = Field(default="📦", max_length=10)
    color: Optional[str] = Field(default="#10b981", max_length=20)
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True, nullable=False)

    # Relación uno a muchos con productos
    products: List["Product"] = Relationship(back_populates="category")

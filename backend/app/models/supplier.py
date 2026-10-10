from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship
from app.models.base import TimestampModel

if TYPE_CHECKING:
    from app.models.product import Product



class Supplier(TimestampModel, table=True):
    """Proveedor de mercadería para la tienda."""
    __tablename__ = "suppliers"

    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str = Field(index=True, max_length=150, nullable=False)
    ruc: str = Field(index=True, unique=True, max_length=20, nullable=False)
    contact_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True, nullable=False)

    # Relaciones
    products: List["Product"] = Relationship(back_populates="supplier")

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
import sqlalchemy as sa
from sqlmodel import Field, Relationship
from app.models.base import TimestampModel

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.supplier import Supplier
    from app.models.inventory import InventoryMovement
    from app.models.sale import SaleItem


class ProductUnit(str, Enum):
    UNIDAD = "und"
    KILOGRAMO = "kg"
    LITRO = "lt"
    PAQUETE = "paq"
    LATA = "lata"
    BOLSA = "bol"



class Product(TimestampModel, table=True):
    """Producto comercializado en Chino Market."""
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.id", index=True, nullable=False)
    supplier_id: Optional[int] = Field(default=None, foreign_key="suppliers.id", index=True)

    name: str = Field(index=True, max_length=150, nullable=False)
    barcode: Optional[str] = Field(default=None, index=True, unique=True, max_length=50)
    sku: str = Field(index=True, unique=True, max_length=30, nullable=False)
    
    unit: ProductUnit = Field(
        default=ProductUnit.UNIDAD,
        sa_column=sa.Column(
            sa.Enum(ProductUnit, native_enum=False, length=20),
            nullable=False
        )
    )

    cost_price: float = Field(default=0.0, ge=0.0, nullable=False)
    sale_price: float = Field(default=0.0, ge=0.0, nullable=False)
    
    current_stock: float = Field(default=0.0, nullable=False)
    min_stock: float = Field(default=5.0, ge=0.0, nullable=False)
    
    expiration_date: Optional[date] = Field(default=None)
    image_url: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True, nullable=False)

    # Relaciones
    category: Optional["Category"] = Relationship(back_populates="products")
    supplier: Optional["Supplier"] = Relationship(back_populates="products")
    inventory_movements: List["InventoryMovement"] = Relationship(back_populates="product")
    sale_items: List["SaleItem"] = Relationship(back_populates="product")

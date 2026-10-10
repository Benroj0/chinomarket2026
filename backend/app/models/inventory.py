from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional
import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.product import Product


class MovementType(str, Enum):
    ENTRADA = "entrada"    # Compra o reabastecimiento
    SALIDA = "salida"      # Venta o consumo interno
    MERMA = "merma"        # Producto vencido, dañado o roto
    AJUSTE = "ajuste"      # Corrección de conteo físico



class InventoryMovement(SQLModel, table=True):
    """Registro de Kárdex y movimientos de stock de productos."""
    __tablename__ = "inventory_movements"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True, nullable=False)
    
    movement_type: MovementType = Field(
        sa_column=sa.Column(
            sa.Enum(MovementType, native_enum=False, length=30),
            nullable=False
        )
    )
    
    quantity: float = Field(nullable=False)
    previous_stock: float = Field(nullable=False)
    new_stock: float = Field(nullable=False)
    
    reference_document: Optional[str] = Field(default=None, max_length=50) # Ej: "BOL-00123", "FACT-458"
    reason: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación
    product: Optional["Product"] = Relationship(back_populates="inventory_movements")

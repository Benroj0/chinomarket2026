from enum import Enum
from typing import TYPE_CHECKING, List, Optional
import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel
from app.models.base import TimestampModel

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.product import Product


class PaymentMethod(str, Enum):
    EFECTIVO = "efectivo"
    YAPE = "yape"
    PLIN = "plin"
    TARJETA = "tarjeta"
    CREDITO = "credito" # Fiado


class SaleStatus(str, Enum):
    COMPLETADA = "completada"
    PENDIENTE = "pendiente"
    ANULADA = "anulada"



class Sale(TimestampModel, table=True):
    """Cabecera de boleta o comprobante de venta."""
    __tablename__ = "sales"

    id: Optional[int] = Field(default=None, primary_key=True)
    receipt_series: str = Field(default="B001", max_length=10, nullable=False)
    receipt_number: int = Field(index=True, nullable=False)
    
    customer_id: Optional[int] = Field(default=None, foreign_key="customers.id", index=True)

    payment_method: PaymentMethod = Field(
        default=PaymentMethod.EFECTIVO,
        sa_column=sa.Column(
            sa.Enum(PaymentMethod, native_enum=False, length=30),
            nullable=False
        )
    )

    status: SaleStatus = Field(
        default=SaleStatus.COMPLETADA,
        sa_column=sa.Column(
            sa.Enum(SaleStatus, native_enum=False, length=30),
            nullable=False
        )
    )

    subtotal: float = Field(default=0.0, ge=0.0, nullable=False)
    tax: float = Field(default=0.0, ge=0.0, nullable=False) # IGV
    discount: float = Field(default=0.0, ge=0.0, nullable=False)
    total: float = Field(default=0.0, ge=0.0, nullable=False)

    cash_received: Optional[float] = Field(default=None)
    cash_change: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=255)

    # Relaciones
    customer: Optional["Customer"] = Relationship(back_populates="sales")
    items: List["SaleItem"] = Relationship(back_populates="sale")


class SaleItem(SQLModel, table=True):
    """Detalle de productos incluidos en una venta."""
    __tablename__ = "sale_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id", index=True, nullable=False)
    product_id: int = Field(foreign_key="products.id", index=True, nullable=False)

    product_name: str = Field(max_length=150, nullable=False)
    unit_price: float = Field(ge=0.0, nullable=False)
    quantity: float = Field(gt=0.0, nullable=False)
    subtotal: float = Field(ge=0.0, nullable=False)

    # Relaciones
    sale: Optional["Sale"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="sale_items")

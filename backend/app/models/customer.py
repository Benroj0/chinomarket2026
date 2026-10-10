from enum import Enum
from typing import TYPE_CHECKING, List, Optional
import sqlalchemy as sa
from sqlmodel import Field, Relationship
from app.models.base import TimestampModel

if TYPE_CHECKING:
    from app.models.sale import Sale


class CustomerType(str, Enum):
    REGULAR = "regular"
    FRECUENTE = "frecuente"
    MAYORISTA = "mayorista"



class Customer(TimestampModel, table=True):
    """Cliente registrado para ventas al detalle, mayoristas o compras al crédito/fiado."""
    __tablename__ = "customers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=150, nullable=False)
    document_type: str = Field(default="DNI", max_length=10) # DNI, RUC, CE
    document_number: Optional[str] = Field(default=None, index=True, max_length=20)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    
    credit_limit: float = Field(default=0.0, ge=0.0, nullable=False)
    current_debt: float = Field(default=0.0, ge=0.0, nullable=False)

    customer_type: CustomerType = Field(
        default=CustomerType.REGULAR,
        sa_column=sa.Column(
            sa.Enum(CustomerType, native_enum=False, length=30),
            nullable=False
        )
    )

    # Relaciones
    sales: List["Sale"] = Relationship(back_populates="customer")

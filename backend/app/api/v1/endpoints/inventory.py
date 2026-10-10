from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.models.inventory import InventoryMovement, MovementType
from app.models.product import Product

router = APIRouter()


class MovementCreate(BaseModel):
    product_id: int
    movement_type: MovementType
    quantity: float
    reference_document: Optional[str] = None
    reason: Optional[str] = None


@router.get("/movements")
async def list_movements(limit: int = 50, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(InventoryMovement, Product.name.label("product_name"), Product.sku.label("product_sku"))
        .outerjoin(Product, InventoryMovement.product_id == Product.id)
        .order_by(InventoryMovement.id.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.all()

    movements = []
    for mov, prod_name, prod_sku in rows:
        m_dict = mov.model_dump()
        m_dict["product_name"] = prod_name or "Desconocido"
        m_dict["product_sku"] = prod_sku or "-"
        movements.append(m_dict)

    return movements


@router.post("/movements", status_code=201)
async def register_movement(payload: MovementCreate, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    old_stock = product.current_stock
    if payload.movement_type in [MovementType.SALIDA, MovementType.MERMA]:
        new_stock = max(0.0, round(old_stock - payload.quantity, 2))
    elif payload.movement_type == MovementType.AJUSTE:
        new_stock = payload.quantity
    else:  # ENTRADA
        new_stock = round(old_stock + payload.quantity, 2)

    product.current_stock = new_stock
    session.add(product)

    movement = InventoryMovement(
        product_id=product.id,
        movement_type=payload.movement_type,
        quantity=payload.quantity,
        previous_stock=old_stock,
        new_stock=new_stock,
        reference_document=payload.reference_document or f"MOV-{product.id}",
        reason=payload.reason or f"Registro de {payload.movement_type.value}"
    )
    session.add(movement)

    await session.commit()
    await session.refresh(movement)

    m_dict = movement.model_dump()
    m_dict["product_name"] = product.name
    return m_dict


@router.get("/alerts")
async def get_low_stock_alerts(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Product)
        .where(Product.is_active == True, Product.current_stock <= Product.min_stock)
        .order_by(Product.current_stock.asc())
    )
    result = await session.execute(stmt)
    products = result.scalars().all()
    return products

from __future__ import annotations

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_

from app.core.database import get_session
from app.models.product import Product, ProductUnit
from app.models.inventory import InventoryMovement, MovementType
from app.models.category import Category

router = APIRouter()


class ProductCreate(BaseModel):
    category_id: int
    name: str
    barcode: Optional[str] = None
    sku: str
    unit: ProductUnit = ProductUnit.UNIDAD
    cost_price: float = 0.0
    sale_price: float
    current_stock: float = 0.0
    min_stock: float = 5.0
    expiration_date: Optional[date] = None
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[ProductUnit] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    current_stock: Optional[float] = None
    min_stock: Optional[float] = None
    expiration_date: Optional[date] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class StockAdjustment(BaseModel):
    quantity: float
    movement_type: MovementType = MovementType.ENTRADA
    reason: Optional[str] = "Ajuste o compra directa"
    reference_document: Optional[str] = None


@router.get("")
async def list_products(
    search: Optional[str] = Query(None, description="Búsqueda por nombre, SKU o código de barras"),
    category_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    low_stock: Optional[bool] = Query(None, description="Filtrar productos con stock <= stock mínimo"),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Product, Category.name.label("category_name")).outerjoin(Category, Product.category_id == Category.id).where(Product.is_active == True)

    if category_id:
        stmt = stmt.where(Product.category_id == category_id)

    if low_stock:
        stmt = stmt.where(Product.current_stock <= Product.min_stock)

    if search:
        search_filter = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(search_filter),
                Product.sku.ilike(search_filter),
                Product.barcode.ilike(search_filter)
            )
        )

    stmt = stmt.order_by(Product.name)
    result = await session.execute(stmt)
    rows = result.all()

    # Formatear respuesta con categoría incluida
    items = []
    for product, cat_name in rows:
        prod_dict = product.model_dump()
        prod_dict["category_name"] = cat_name or "Sin Categoría"
        items.append(prod_dict)

    return items


@router.get("/{product_id}")
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("", status_code=201)
async def create_product(payload: ProductCreate, session: AsyncSession = Depends(get_session)):
    # Validar SKU único
    existing_sku = await session.execute(select(Product).where(Product.sku == payload.sku, Product.is_active == True))
    if existing_sku.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El código SKU ya está registrado.")

    # Validar código de barras si viene
    if payload.barcode:
        existing_bc = await session.execute(select(Product).where(Product.barcode == payload.barcode, Product.is_active == True))
        if existing_bc.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="El código de barras ya está registrado.")

    product = Product(
        category_id=payload.category_id,
        name=payload.name,
        barcode=payload.barcode,
        sku=payload.sku.upper(),
        unit=payload.unit,
        cost_price=payload.cost_price,
        sale_price=payload.sale_price,
        current_stock=payload.current_stock,
        min_stock=payload.min_stock,
        expiration_date=payload.expiration_date,
        image_url=payload.image_url,
        is_active=True,
    )
    session.add(product)
    await session.flush()

    # Registrar movimiento inicial en Kárdex si stock > 0
    if payload.current_stock > 0:
        movement = InventoryMovement(
            product_id=product.id,
            movement_type=MovementType.ENTRADA,
            quantity=payload.current_stock,
            previous_stock=0.0,
            new_stock=payload.current_stock,
            reason="Inventario inicial al crear producto",
            reference_document=f"INIT-{product.sku}"
        )
        session.add(movement)

    await session.commit()
    await session.refresh(product)
    return product


@router.put("/{product_id}")
async def update_product(product_id: int, payload: ProductUpdate, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.patch("/{product_id}/stock")
async def adjust_stock(product_id: int, payload: StockAdjustment, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    old_stock = product.current_stock
    if payload.movement_type in [MovementType.SALIDA, MovementType.MERMA]:
        new_stock = max(0.0, old_stock - payload.quantity)
    else:
        new_stock = old_stock + payload.quantity

    product.current_stock = new_stock
    session.add(product)

    movement = InventoryMovement(
        product_id=product.id,
        movement_type=payload.movement_type,
        quantity=payload.quantity,
        previous_stock=old_stock,
        new_stock=new_stock,
        reason=payload.reason,
        reference_document=payload.reference_document or f"AJUSTE-{product.id}"
    )
    session.add(movement)

    await session.commit()
    await session.refresh(product)
    return {
        "product_id": product.id,
        "previous_stock": old_stock,
        "new_stock": new_stock,
        "movement": payload.movement_type
    }


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    product.is_active = False
    session.add(product)
    await session.commit()
    return None

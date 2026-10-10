from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.core.database import get_session
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.product import Product
from app.models.customer import Customer
from app.models.inventory import InventoryMovement, MovementType

router = APIRouter()


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    payment_method: PaymentMethod = PaymentMethod.EFECTIVO
    items: List[SaleItemCreate]
    cash_received: Optional[float] = None
    discount: float = 0.0
    notes: Optional[str] = None


@router.get("")
async def list_sales(session: AsyncSession = Depends(get_session)):
    stmt = select(Sale, Customer.name.label("customer_name")).outerjoin(Customer, Sale.customer_id == Customer.id).order_by(Sale.id.desc()).limit(50)
    result = await session.execute(stmt)
    rows = result.all()

    sales_list = []
    for sale, cust_name in rows:
        # Traer items de la venta
        items_stmt = select(SaleItem).where(SaleItem.sale_id == sale.id)
        items_res = await session.execute(items_stmt)
        items = items_res.scalars().all()

        s_dict = sale.model_dump()
        s_dict["customer_name"] = cust_name or "Cliente General"
        s_dict["items"] = [item.model_dump() for item in items]
        sales_list.append(s_dict)

    return sales_list


@router.get("/{sale_id}")
async def get_sale(sale_id: int, session: AsyncSession = Depends(get_session)):
    sale = await session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    items_stmt = select(SaleItem).where(SaleItem.sale_id == sale.id)
    items_res = await session.execute(items_stmt)
    items = items_res.scalars().all()

    cust_name = "Cliente General"
    if sale.customer_id:
        cust = await session.get(Customer, sale.customer_id)
        if cust:
            cust_name = cust.name

    s_dict = sale.model_dump()
    s_dict["customer_name"] = cust_name
    s_dict["items"] = [item.model_dump() for item in items]
    return s_dict


@router.post("", status_code=201)
async def create_sale(payload: SaleCreate, session: AsyncSession = Depends(get_session)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="La venta debe incluir al menos un producto.")

    # Generar correlativo de boleta
    count_stmt = select(func.count(Sale.id))
    current_count = (await session.execute(count_stmt)).scalar() or 0
    receipt_number = current_count + 1
    receipt_series = "B001"

    # Calcular montos
    subtotal = 0.0
    sale_items = []

    for item_data in payload.items:
        prod = await session.get(Product, item_data.product_id)
        if not prod or not prod.is_active:
            raise HTTPException(status_code=404, detail=f"Producto #{item_data.product_id} no disponible.")

        if prod.current_stock < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{prod.name}'. Disponible: {prod.current_stock}, solicitado: {item_data.quantity}"
            )

        item_subtotal = round(item_data.quantity * item_data.unit_price, 2)
        subtotal += item_subtotal

        # Descontar stock
        old_stock = prod.current_stock
        new_stock = round(old_stock - item_data.quantity, 2)
        prod.current_stock = new_stock
        session.add(prod)

        # Movimiento de Kárdex
        movement = InventoryMovement(
            product_id=prod.id,
            movement_type=MovementType.SALIDA,
            quantity=item_data.quantity,
            previous_stock=old_stock,
            new_stock=new_stock,
            reason="Venta en mostrador (POS)",
            reference_document=f"{receipt_series}-{receipt_number:06d}"
        )
        session.add(movement)

        # Ítem de venta
        sale_items.append(
            SaleItem(
                product_id=prod.id,
                product_name=prod.name,
                unit_price=item_data.unit_price,
                quantity=item_data.quantity,
                subtotal=item_subtotal
            )
        )

    # Impuestos y total
    total = max(0.0, round(subtotal - payload.discount, 2))
    tax = round(total * 0.18 / 1.18, 2) # IGV 18% incluido
    subtotal_sin_igv = round(total - tax, 2)

    # Vuelto si es efectivo
    cash_change = None
    if payload.payment_method == PaymentMethod.EFECTIVO and payload.cash_received:
        cash_change = max(0.0, round(payload.cash_received - total, 2))

    # Manejar fiado (crédito)
    if payload.payment_method == PaymentMethod.CREDITO:
        if not payload.customer_id:
            raise HTTPException(status_code=400, detail="Debe seleccionar un cliente para registrar una venta al crédito (Fiado).")
        customer = await session.get(Customer, payload.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")
        customer.current_debt = round(customer.current_debt + total, 2)
        session.add(customer)

    sale = Sale(
        receipt_series=receipt_series,
        receipt_number=receipt_number,
        customer_id=payload.customer_id,
        payment_method=payload.payment_method,
        status=SaleStatus.COMPLETADA,
        subtotal=subtotal_sin_igv,
        tax=tax,
        discount=payload.discount,
        total=total,
        cash_received=payload.cash_received,
        cash_change=cash_change,
        notes=payload.notes
    )
    session.add(sale)
    await session.flush()

    for s_item in sale_items:
        s_item.sale_id = sale.id
        session.add(s_item)

    await session.commit()
    await session.refresh(sale)

    return {
        "id": sale.id,
        "receipt": f"{sale.receipt_series}-{sale.receipt_number:06d}",
        "total": sale.total,
        "payment_method": sale.payment_method,
        "cash_change": sale.cash_change,
        "items_count": len(sale_items)
    }

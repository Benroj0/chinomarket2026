from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.core.database import get_session
from app.models.product import Product
from app.models.sale import Sale
from app.models.customer import Customer
from app.models.inventory import InventoryMovement

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(session: AsyncSession = Depends(get_session)):
    # Total productos activos
    prod_stmt = select(func.count(Product.id)).where(Product.is_active == True)
    total_products = (await session.execute(prod_stmt)).scalar() or 0

    # Alertas stock bajo
    alert_stmt = select(func.count(Product.id)).where(Product.is_active == True, Product.current_stock <= Product.min_stock)
    low_stock_alerts = (await session.execute(alert_stmt)).scalar() or 0

    # Ventas totales
    sales_count_stmt = select(func.count(Sale.id))
    today_sales_count = (await session.execute(sales_count_stmt)).scalar() or 0

    sales_total_stmt = select(func.sum(Sale.total))
    today_sales_total = (await session.execute(sales_total_stmt)).scalar() or 0.0

    # Total por cobrar (fiados)
    debt_stmt = select(func.sum(Customer.current_debt))
    total_receivable_debt = (await session.execute(debt_stmt)).scalar() or 0.0

    return {
        "total_products": total_products,
        "low_stock_alerts": low_stock_alerts,
        "today_sales_count": today_sales_count,
        "today_sales_total": round(float(today_sales_total), 2),
        "total_receivable_debt": round(float(total_receivable_debt), 2)
    }

from __future__ import annotations

from fastapi import APIRouter
from app.api.v1.endpoints import categories, products, sales, inventory, customers, dashboard

api_router = APIRouter()

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categorías"])
api_router.include_router(products.router, prefix="/products", tags=["Productos"])
api_router.include_router(sales.router, prefix="/sales", tags=["Ventas & POS"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventario & Kárdex"])
api_router.include_router(customers.router, prefix="/customers", tags=["Clientes & Fiados"])

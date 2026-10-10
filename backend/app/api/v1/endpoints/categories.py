from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.models.category import Category

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    code: str
    icon: Optional[str] = "🏷️"
    color: Optional[str] = "emerald"
    description: Optional[str] = None
    is_active: bool = True


@router.get("", response_model=List[Category])
async def list_categories(session: AsyncSession = Depends(get_session)):
    stmt = select(Category).where(Category.is_active == True).order_by(Category.name)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=Category, status_code=201)
async def create_category(payload: CategoryCreate, session: AsyncSession = Depends(get_session)):
    # Check if code already exists
    existing = await session.execute(select(Category).where(Category.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El código de categoría ya existe.")

    category = Category(
        name=payload.name,
        code=payload.code.upper(),
        icon=payload.icon,
        color=payload.color,
        description=payload.description,
        is_active=payload.is_active,
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session)):
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    category.is_active = False
    session.add(category)
    await session.commit()
    return None

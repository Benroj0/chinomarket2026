from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.models.customer import Customer, CustomerType

router = APIRouter()


class CustomerCreate(BaseModel):
    name: str
    document_type: str = "DNI"
    document_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    credit_limit: float = 100.0
    customer_type: CustomerType = CustomerType.REGULAR


class DebtPayment(BaseModel):
    amount: float
    notes: Optional[str] = "Abono en efectivo a cuenta fiada"


@router.get("", response_model=List[Customer])
async def list_customers(session: AsyncSession = Depends(get_session)):
    stmt = select(Customer).order_by(Customer.current_debt.desc(), Customer.name.asc())
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=Customer, status_code=201)
async def create_customer(payload: CustomerCreate, session: AsyncSession = Depends(get_session)):
    customer = Customer(
        name=payload.name,
        document_type=payload.document_type,
        document_number=payload.document_number,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        credit_limit=payload.credit_limit,
        current_debt=0.0,
        customer_type=payload.customer_type,
    )
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


@router.post("/{customer_id}/pay-debt")
async def pay_debt(customer_id: int, payload: DebtPayment, session: AsyncSession = Depends(get_session)):
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="El monto del abono debe ser mayor a 0")

    old_debt = customer.current_debt
    new_debt = max(0.0, round(old_debt - payload.amount, 2))
    customer.current_debt = new_debt

    session.add(customer)
    await session.commit()
    await session.refresh(customer)

    return {
        "customer_id": customer.id,
        "name": customer.name,
        "amount_paid": payload.amount,
        "previous_debt": old_debt,
        "current_debt": new_debt
    }

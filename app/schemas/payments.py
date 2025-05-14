from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "Cash"
    CHECK = "Check"
    CREDIT_CARD = "Credit Card"
    BANK_TRANSFER = "Bank Transfer"
    MPESA = "MPESA"
    OTHER = "Other"

class PaymentBase(BaseModel):
    amount: float
    payment_method: PaymentMethod
    invoice_id: int
    payment_reference: Optional[str] = None
    payment_date: Optional[datetime] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    payment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

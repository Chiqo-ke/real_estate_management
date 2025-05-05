from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "Cash"
    CHECK = "Check"
    CREDIT_CARD = "Credit Card"
    BANK_TRANSFER = "Bank Transfer"
    OTHER = "Other"

class PaymentBase(BaseModel):
    amount: float
    payment_method: PaymentMethod
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    invoice_id: int

class PaymentResponse(PaymentBase):
    payment_id: int
    invoice_id: int
    payment_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from typing import List
from ..database import get_db
from ..models.user import User
from app.models.payment import Payment
from ..schemas import PaymentCreate, PaymentResponse
from .auth import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/")
async def get_payments(db: Session = Depends(get_db)):
    query = text("""
        SELECT p.*, i.amount as invoice_amount, i.status as invoice_status,
               l.unit_number, pr.name as property_name,
               t.first_name, t.last_name
        FROM payments p
        JOIN invoices i ON p.invoice_id = i.invoice_id
        JOIN leases l ON i.lease_id = l.lease_id
        JOIN properties pr ON l.property_id = pr.property_id
        JOIN tenants t ON l.tenant_id = t.tenant_id
        ORDER BY p.payment_date DESC
    """)
    results = db.execute(query).fetchall()
    return [dict(row._mapping) for row in results]

@router.post("/{invoice_id}")
async def record_payment(
    invoice_id: int,
    amount: float,
    payment_method: str,
    reference_number: str = None,
    db: Session = Depends(get_db)
):
    try:
        # Start transaction
        db.execute(text("BEGIN"))
        
        # Check invoice exists and get current status
        invoice = db.execute(
            text("SELECT amount, status FROM invoices WHERE invoice_id = :id"),
            {"id": invoice_id}
        ).fetchone()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Record payment
        payment_query = text("""
            INSERT INTO payments (invoice_id, payment_date, amount, 
                                payment_method, reference_number)
            VALUES (:invoice_id, CURRENT_DATE, :amount, :method, :reference)
        """)
        
        db.execute(payment_query, {
            "invoice_id": invoice_id,
            "amount": amount,
            "method": payment_method,
            "reference": reference_number
        })
        
        # Calculate total payments for this invoice
        total_paid = db.execute(
            text("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM payments
                WHERE invoice_id = :id
            """),
            {"id": invoice_id}
        ).fetchone().total + amount
        
        # Update invoice status
        new_status = (
            'Paid' if total_paid >= invoice.amount
            else 'Partially Paid' if total_paid > 0
            else 'Pending'
        )
        
        db.execute(
            text("""
                UPDATE invoices 
                SET status = :status
                WHERE invoice_id = :id
            """),
            {"id": invoice_id, "status": new_status}
        )
        
        db.execute(text("COMMIT"))
        return {"message": "Payment recorded successfully", "new_status": new_status}
        
    except Exception as e:
        db.execute(text("ROLLBACK"))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary")
async def get_payment_summary(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            p.name as property_name,
            COUNT(DISTINCT l.lease_id) as total_active_leases,
            COUNT(i.invoice_id) as total_invoices,
            SUM(CASE WHEN i.status = 'Pending' THEN i.amount ELSE 0 END) as total_pending,
            SUM(CASE WHEN i.status = 'Paid' THEN i.amount ELSE 0 END) as total_paid
        FROM properties p
        LEFT JOIN leases l ON p.property_id = l.property_id AND l.lease_status = 'Active'
        LEFT JOIN invoices i ON l.lease_id = i.lease_id
        GROUP BY p.property_id, p.name
    """)
    results = db.execute(query).fetchall()
    return [dict(row._mapping) for row in results]

@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify if the user is the tenant making the payment
    if current_user.id != payment.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="You can only make payments for your own leases"
        )
    
    db_payment = Payment(
        amount=payment.amount,
        lease_id=payment.lease_id,
        tenant_id=current_user.id,
        payment_method=payment.payment_method,
        status="pending"
    )
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Payment).filter(Payment.tenant_id == current_user.id).all()

@router.post("/rent", response_model=PaymentResponse)
async def pay_rent(
    payment: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Start transaction
        db.execute(text("BEGIN"))
        
        # Verify invoice belongs to the tenant
        invoice = db.execute(
            text("""
                SELECT i.*, l.tenant_id, l.monthly_rent
                FROM invoices i
                JOIN leases l ON i.lease_id = l.lease_id
                WHERE i.invoice_id = :invoice_id
            """),
            {"invoice_id": payment.invoice_id}
        ).fetchone()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        # Verify tenant owns this invoice
        tenant = db.execute(
            text("SELECT tenant_id FROM tenants WHERE email = :email"),
            {"email": current_user.email}
        ).fetchone()
        
        if invoice.tenant_id != tenant.tenant_id:
            raise HTTPException(
                status_code=403,
                detail="You can only pay your own invoices"
            )
        
        # Validate payment amount
        if payment.amount <= 0 or payment.amount > invoice.amount:
            raise HTTPException(
                status_code=400,
                detail="Invalid payment amount"
            )
        
        # Record payment
        result = db.execute(
            text("""
                INSERT INTO payments (
                    invoice_id, payment_date, amount, 
                    payment_method, reference_number, status
                )
                VALUES (
                    :invoice_id, CURRENT_DATE, :amount,
                    :method, :reference, 'completed'
                )
                RETURNING *
            """),
            {
                "invoice_id": payment.invoice_id,
                "amount": payment.amount,
                "method": payment.payment_method,
                "reference": payment.reference_number
            }
        )
        
        # Update invoice status
        total_paid = db.execute(
            text("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM payments
                WHERE invoice_id = :id
            """),
            {"id": payment.invoice_id}
        ).fetchone().total + payment.amount
        
        new_status = (
            'Paid' if total_paid >= invoice.amount
            else 'Partially Paid' if total_paid > 0
            else 'Pending'
        )
        
        db.execute(
            text("""
                UPDATE invoices 
                SET status = :status
                WHERE invoice_id = :id
            """),
            {"id": payment.invoice_id, "status": new_status}
        )
        
        db.execute(text("COMMIT"))
        payment_record = result.fetchone()
        return dict(payment_record._mapping)
        
    except Exception as e:
        db.execute(text("ROLLBACK"))
        raise HTTPException(status_code=400, detail=str(e))

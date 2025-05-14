from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter(
    prefix="/debts",
    tags=["debts"]
)

@router.get("/occupied")
async def get_occupied_debts(db: Session = Depends(get_db)):
    """
    Returns a list of currently occupied properties with their outstanding debts.
    Each item includes property details, tenant information, and the amount owed.
    """
    query = text("""
        SELECT 
            p.property_id,
            p.name as property_name,
            p.address,
            l.unit_number,
            CONCAT(t.first_name, ' ', t.last_name) as tenant_name,
            t.email as tenant_email,
            t.phone as tenant_phone,
            SUM(CASE 
                WHEN i.status IN ('Pending', 'Partially Paid') 
                THEN i.amount - COALESCE(
                    (SELECT SUM(amount) FROM payments WHERE invoice_id = i.invoice_id), 
                    0
                )
                ELSE 0 
            END) as outstanding_amount,
            MAX(pay.payment_date) as last_payment_date
        FROM properties p
        JOIN leases l ON p.property_id = l.property_id
        JOIN tenants t ON l.tenant_id = t.tenant_id
        LEFT JOIN invoices i ON l.lease_id = i.lease_id
        LEFT JOIN payments pay ON i.invoice_id = pay.invoice_id
        WHERE l.lease_status = 'Active'
        GROUP BY p.property_id, p.name, p.address, l.unit_number, t.first_name, t.last_name, t.email, t.phone
        HAVING outstanding_amount > 0
        ORDER BY outstanding_amount DESC
    """)
    
    results = db.execute(query).fetchall()
    return {
        "occupied_debts": [
            {
                "property_id": row.property_id,
                "property_name": row.property_name,
                "address": row.address,
                "unit_number": row.unit_number,
                "tenant_name": row.tenant_name,
                "tenant_email": row.tenant_email,
                "tenant_phone": row.tenant_phone,
                "outstanding_amount": float(row.outstanding_amount),
                "last_payment_date": row.last_payment_date.isoformat() if row.last_payment_date else None
            }
            for row in results
        ]
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from ..database import get_db

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/")
async def get_invoices(db: Session = Depends(get_db)):
    query = text("""
        SELECT i.*, l.unit_number, p.name as property_name, 
               t.first_name, t.last_name
        FROM invoices i
        JOIN leases l ON i.lease_id = l.lease_id
        JOIN properties p ON l.property_id = p.property_id
        JOIN tenants t ON l.tenant_id = t.tenant_id
        ORDER BY i.due_date DESC
    """)
    results = db.execute(query).fetchall()
    return [dict(row._mapping) for row in results]

@router.post("/generate-monthly")
async def generate_monthly_invoices(db: Session = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO invoices (lease_id, invoice_date, due_date, amount, description, status)
            SELECT 
                l.lease_id,
                CURRENT_DATE,
                DATE_ADD(CURRENT_DATE, INTERVAL 1 MONTH),
                l.monthly_rent,
                CONCAT('Monthly rent for ', DATE_FORMAT(DATE_ADD(CURRENT_DATE, INTERVAL 1 MONTH), '%M %Y')),
                'Pending'
            FROM leases l
            WHERE l.lease_status = 'Active'
            AND NOT EXISTS (
                SELECT 1 FROM invoices i 
                WHERE i.lease_id = l.lease_id 
                AND MONTH(i.due_date) = MONTH(DATE_ADD(CURRENT_DATE, INTERVAL 1 MONTH))
                AND YEAR(i.due_date) = YEAR(DATE_ADD(CURRENT_DATE, INTERVAL 1 MONTH))
            )
        """)
        db.execute(query)
        db.commit()
        return {"message": "Monthly invoices generated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/overdue")
async def get_overdue_invoices(db: Session = Depends(get_db)):
    query = text("""
        SELECT i.*, l.unit_number, p.name as property_name,
               t.first_name, t.last_name, t.email
        FROM invoices i
        JOIN leases l ON i.lease_id = l.lease_id
        JOIN properties p ON l.property_id = p.property_id
        JOIN tenants t ON l.tenant_id = t.tenant_id
        WHERE i.status = 'Pending'
        AND i.due_date < CURRENT_DATE
        ORDER BY i.due_date
    """)
    results = db.execute(query).fetchall()
    return [dict(row._mapping) for row in results]

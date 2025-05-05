from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from ..database import get_db
from ..schemas.properties import PropertyCreate, Property

router = APIRouter(prefix="/properties", tags=["properties"])

@router.get("/", response_model=List[Property])
async def get_properties(db: Session = Depends(get_db)):
    properties = db.execute(text("SELECT * FROM properties")).fetchall()
    return [dict(prop._mapping) for prop in properties]

@router.post("/", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property(property: PropertyCreate, db: Session = Depends(get_db)):
    query = text("""
        INSERT INTO properties 
        (name, address, city, state, zip_code, property_type, total_units, available_units)
        VALUES 
        (:name, :address, :city, :state, :zip_code, :property_type, :total_units, :available_units)
    """)
    
    try:
        result = db.execute(query, property.model_dump())
        db.commit()
        
        # Fetch the created property
        new_property = db.execute(
            text("SELECT * FROM properties WHERE property_id = :id"),
            {"id": result.lastrowid}
        ).fetchone()
        
        return dict(new_property._mapping)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{property_id}/occupancy")
async def get_property_occupancy(property_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT p.*, 
               COUNT(l.lease_id) as occupied_units,
               p.total_units - COUNT(l.lease_id) as available_units
        FROM properties p
        LEFT JOIN leases l ON p.property_id = l.property_id 
        WHERE p.property_id = :property_id AND l.lease_status = 'Active'
        GROUP BY p.property_id
    """)
    result = db.execute(query, {"property_id": property_id}).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Property not found")
    return dict(result._mapping)

@router.get("/{property_id}/units")
async def get_property_units(property_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT l.unit_number, 
               CASE 
                   WHEN l.lease_status = 'Active' THEN 'Occupied'
                   ELSE 'Available'
               END as status,
               t.first_name, 
               t.last_name
        FROM properties p
        LEFT JOIN leases l ON p.property_id = l.property_id
        LEFT JOIN tenants t ON l.tenant_id = t.tenant_id
        WHERE p.property_id = :property_id
    """)
    results = db.execute(query, {"property_id": property_id}).fetchall()
    return [dict(row._mapping) for row in results]

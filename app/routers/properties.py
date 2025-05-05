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

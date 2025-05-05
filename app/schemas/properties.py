from pydantic import BaseModel
from typing import Literal

class PropertyCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: Literal['Apartment', 'House', 'Condo', 'Commercial']
    total_units: int
    available_units: int

class Property(PropertyCreate):
    property_id: int
    class Config:
        from_attributes = True
